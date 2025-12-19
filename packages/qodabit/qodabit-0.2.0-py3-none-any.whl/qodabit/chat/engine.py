"""Chat REPL engine."""

import asyncio
import re
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from qodabit.ai.client import AIClient, apply_fix, get_code_context, get_line_content
from qodabit.scanner.orchestrator import (
    Issue,
    ScanResult,
    count_by_severity,
    scan_project,
)
from qodabit.score.calculator import calculate_score

# Load environment variables
load_dotenv()

console = Console()

# Store last scan results for reference
_last_scan: Optional[ScanResult] = None
_issues_by_id: Dict[str, Issue] = {}
_ai_client: Optional[AIClient] = None


def _get_ai_client() -> AIClient:
    """Get or create AI client."""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


def parse_natural_language(user_input: str) -> Tuple[str, Optional[str]]:
    """Parse natural language input and return (intent, argument).

    Intents:
    - scan: Run security scan
    - scan_path: Scan specific path
    - explain: Explain an issue
    - fix: Fix an issue
    - score: Show score
    - issues: List issues
    - help: Show help
    - exit: Exit chat
    - unknown: Unknown intent

    Returns:
        (intent, argument) tuple
    """
    text = user_input.lower().strip()

    # Exit patterns
    if text in ("salir", "exit", "quit", "bye", "adios", "adiós"):
        return ("exit", None)

    # Help patterns
    if text in ("ayuda", "help", "?", "comandos"):
        return ("help", None)

    # Score patterns (be specific to avoid matching scan patterns)
    score_patterns = [
        r"^score$",
        r"qué tan (listo|preparado)",
        r"production.?ready",
        r"puntuación|puntaje|calificación",
    ]
    for pattern in score_patterns:
        if re.search(pattern, text):
            return ("score", None)

    # Issues list patterns
    issues_patterns = [
        r"^(issues|lista|problemas)$",
        r"(lista|muestra|ver|dame).*(issues|problemas|vulnerabilidades)",
        r"qué (issues|problemas|vulnerabilidades) (hay|tiene|existen)",
        r"cuáles son los (issues|problemas)",
    ]
    for pattern in issues_patterns:
        if re.search(pattern, text):
            return ("issues", None)

    # Fix patterns - check for issue ID or keyword
    fix_patterns = [
        r"^fix\s+(.+)$",
        r"^arregla\s+(.+)$",
        r"^corrige\s+(.+)$",
        r"^repara\s+(.+)$",
        r"(arregla|corrige|repara|soluciona).*(sec-\w+)",
    ]
    for pattern in fix_patterns:
        match = re.search(pattern, text)
        if match:
            # Extract issue ID or search term
            arg = match.group(1) if match.lastindex else match.group(2)
            return (
                "fix",
                arg.strip().upper() if arg.startswith("sec") else arg.strip(),
            )

    # Explain patterns - check for issue ID or topic
    # First check for SEC-XXX ID anywhere in the text
    id_match = re.search(r"sec-\w+", text, re.IGNORECASE)
    if id_match:
        explain_triggers = [
            r"explica",
            r"explicar",
            r"explícame",
            r"qué es",
            r"cómo (arreglo|soluciono|corrijo)",
        ]
        for trigger in explain_triggers:
            if re.search(trigger, text):
                return ("explain", id_match.group(0).upper())

    # Topic-based explain patterns
    explain_topic_patterns = [
        r"^explica\s+(.+)$",
        r"^explicar\s+(.+)$",
        r"qué es (?:un |una |el |la )?(.+?)(?:\?|$)",
        r"cómo (?:arreglo|soluciono|corrijo) (?:el |la |un |una )?(.+?)(?:\?|$)",
    ]
    for pattern in explain_topic_patterns:
        match = re.search(pattern, text)
        if match:
            topic = match.group(1).strip()
            if topic:
                return ("explain_topic", topic)

    # Scan with path patterns
    path_patterns = [
        (r"^analiza\s+solo\s+(.+)$", 1),  # "analiza solo src/auth.py"
        (r"^analiza\s+el archivo\s+(.+)$", 1),  # "analiza el archivo src/db.py"
        (r"^analiza\s+la carpeta\s+(.+)$", 1),  # "analiza la carpeta src/"
        (r"^analiza\s+(\S+\.\w+)$", 1),  # "analiza file.py"
        (r"^analiza\s+(\S+/)$", 1),  # "analiza src/"
        (r"^scan\s+(.+)$", 1),
        (r"^escanea\s+(.+)$", 1),
        (r"^revisa\s+(.+)$", 1),
        (r"está seguro (.+\.\w+)", 1),
        (r"problemas (?:en|de) (.+\.\w+|\S+/)", 1),
    ]
    for pattern, group_idx in path_patterns:
        match = re.search(pattern, text)
        if match:
            path = match.group(group_idx)
            if path and not path.startswith(("el ", "la ", "mi ", "este ")):
                return ("scan_path", path.strip())

    # General scan patterns
    scan_patterns = [
        r"^(analiza|scan|escanea|revisa)$",
        r"qué problemas tiene",
        r"analiza (mi |el )?(código|proyecto|repositorio)",
        r"escanea (mi |el )?(código|proyecto)",
        r"hay (vulnerabilidades|problemas|issues)",
        r"revisa (mi |el )?(código|proyecto)",
        r"está seguro (mi |el )?(código|proyecto)",
        r"tiene (vulnerabilidades|problemas|issues)",
    ]
    for pattern in scan_patterns:
        if re.search(pattern, text):
            return ("scan", None)

    # Unknown - but might be a question about security
    if "?" in text or text.startswith(("qué", "cómo", "por qué", "cuál")):
        return ("question", user_input)

    return ("unknown", user_input)


def find_issue_by_topic(topic: str) -> Optional[str]:
    """Find an issue ID by topic keyword (e.g., 'sql injection').

    When multiple issues match, returns the one with highest severity.
    Priority: CRITICAL > HIGH > MEDIUM > LOW
    """
    global _issues_by_id

    if not _issues_by_id:
        return None

    topic_lower = topic.lower().replace("-", " ").replace("_", " ")
    severity_priority = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    matches: list[tuple[int, str, Issue]] = []

    for issue_id, issue in _issues_by_id.items():
        # Check in rule name, message, or file
        searchable = f"{issue.rule} {issue.message} {issue.file}".lower()
        if topic_lower in searchable:
            priority = severity_priority.get(issue.severity, 4)
            matches.append((priority, issue_id, issue))

    if not matches:
        return None

    # Sort by severity priority (lowest number = highest priority)
    matches.sort(key=lambda x: x[0])
    return matches[0][1]


def start_chat() -> None:
    """Start interactive chat mode."""
    console.print(
        Panel(
            "[bold cyan]QodaBit v0.2.0[/bold cyan] - Security Copilot\n"
            "[dim]Escribe 'ayuda' para ver comandos o pregunta en español[/dim]",
            title="QodaBit",
            border_style="cyan",
        )
    )

    while True:
        try:
            user_input = console.input("\n[bold green]>[/bold green] ").strip()

            if not user_input:
                continue

            # Parse natural language input
            intent, arg = parse_natural_language(user_input)

            if intent == "exit":
                console.print("\n[dim]Hasta luego![/dim]")
                break

            elif intent == "help":
                show_help()

            elif intent == "scan":
                asyncio.run(run_scan())

            elif intent == "scan_path":
                asyncio.run(run_scan(arg))

            elif intent == "score":
                show_score()

            elif intent == "issues":
                show_issues()

            elif intent == "explain":
                explain_issue(arg)

            elif intent == "explain_topic":
                # Try to find an issue by topic
                issue_id = find_issue_by_topic(arg) if arg else None
                if issue_id:
                    console.print(f"[dim]Encontré issue relacionado: {issue_id}[/dim]")
                    explain_issue(issue_id)
                else:
                    console.print(f"[yellow]No encontré issue sobre '{arg}'.[/yellow]")
                    console.print(
                        "[dim]Usa 'analiza' primero o especifica el ID del issue.[/dim]"
                    )

            elif intent == "fix":
                # Check if arg is an issue ID or a topic
                if arg and arg.startswith("SEC-"):
                    fix_issue(arg)
                else:
                    # Try to find issue by topic
                    issue_id = find_issue_by_topic(arg) if arg else None
                    if issue_id:
                        console.print(
                            f"[dim]Encontré issue relacionado: {issue_id}[/dim]"
                        )
                        fix_issue(issue_id)
                    else:
                        console.print(
                            f"[yellow]No encontré issue sobre '{arg}'.[/yellow]"
                        )
                        console.print(
                            "[dim]Usa 'issues' para ver la lista de issues.[/dim]"
                        )

            elif intent == "question":
                # General question - suggest running scan first
                console.print(
                    "[dim]Para responder preguntas sobre tu código, "
                    "primero necesito analizarlo.[/dim]"
                )
                console.print("[dim]Escribe 'analiza' para comenzar.[/dim]")

            else:
                # Unknown command
                console.print(f"[dim]No entendí: {user_input}[/dim]")
                console.print("[dim]Escribe 'ayuda' o pregunta en español.[/dim]")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Hasta luego![/dim]")
            break


async def run_scan(path: str = ".") -> None:
    """Run security scan and display results."""
    global _last_scan, _issues_by_id

    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Escaneando proyecto...", total=None)

        # Run the scan
        result = await scan_project(path)
        _last_scan = result

        # Index issues by ID for quick lookup
        _issues_by_id = {issue.id: issue for issue in result.issues}

        progress.update(task, completed=True)

    # Show scan summary
    console.print()
    for tool in result.tools_run:
        console.print(f"[green]✓[/green] {tool}")

    if result.errors:
        for error in result.errors:
            console.print(f"[yellow]⚠[/yellow] {error}")

    console.print(f"\n[dim]Tiempo: {result.duration_ms}ms[/dim]")

    # Calculate and show score
    issues_dicts = [{"severity": i.severity} for i in result.issues]
    score_result = calculate_score(issues_dicts)

    # Score color based on category
    score_color = {
        "PRODUCTION_READY": "green",
        "ALMOST_READY": "yellow",
        "NEEDS_WORK": "orange1",
        "NOT_READY": "red",
    }.get(score_result.category, "white")

    console.print()
    console.print(
        Panel(
            f"[bold {score_color}]Production-Ready Score: {score_result.score}%[/bold {score_color}]",
            border_style=score_color,
        )
    )

    # Show issues by severity
    if result.issues:
        show_issues_summary(result.issues)
    else:
        console.print("\n[green]✓ No se encontraron issues de seguridad[/green]")


def show_issues_summary(issues: List[Issue]) -> None:
    """Show issues grouped by severity."""
    counts = count_by_severity(issues)

    severity_config = {
        "CRITICAL": {"color": "red", "emoji": "🔴"},
        "HIGH": {"color": "orange1", "emoji": "🟠"},
        "MEDIUM": {"color": "yellow", "emoji": "🟡"},
        "LOW": {"color": "dim", "emoji": "⚪"},
    }

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if counts[severity] == 0:
            continue

        config = severity_config[severity]
        console.print(
            f"\n{config['emoji']} [{config['color']}]{severity} ({counts[severity]})[/{config['color']}]"
        )

        # Show issues of this severity
        for issue in issues:
            if issue.severity == severity:
                console.print(
                    f"   [{config['color']}]{issue.id}[/{config['color']}]  {issue.message[:40]:<40}  [dim]{issue.file}:{issue.line}[/dim]"
                )


def show_score() -> None:
    """Show current Production-Ready Score."""
    global _last_scan

    if not _last_scan:
        console.print("[yellow]No hay scan reciente. Usa 'analiza' primero.[/yellow]")
        return

    issues_dicts = [{"severity": i.severity} for i in _last_scan.issues]
    score_result = calculate_score(issues_dicts)

    score_color = {
        "PRODUCTION_READY": "green",
        "ALMOST_READY": "yellow",
        "NEEDS_WORK": "orange1",
        "NOT_READY": "red",
    }.get(score_result.category, "white")

    console.print(
        Panel(
            f"[bold {score_color}]Production-Ready Score: {score_result.score}%[/bold {score_color}]",
            border_style=score_color,
        )
    )


def show_issues() -> None:
    """Show all issues from last scan."""
    global _last_scan

    if not _last_scan:
        console.print("[yellow]No hay scan reciente. Usa 'analiza' primero.[/yellow]")
        return

    if not _last_scan.issues:
        console.print("[green]✓ No hay issues pendientes[/green]")
        return

    show_issues_summary(_last_scan.issues)


def explain_issue(issue_id: str) -> None:
    """Explain a security issue using AI."""
    global _issues_by_id

    if not _issues_by_id:
        console.print("[yellow]No hay scan reciente. Usa 'analiza' primero.[/yellow]")
        return

    # Find the issue
    issue = _issues_by_id.get(issue_id)
    if not issue:
        console.print(f"[red]Issue '{issue_id}' no encontrado.[/red]")
        console.print("[dim]Usa 'issues' para ver la lista de issues.[/dim]")
        return

    console.print()
    console.print(
        Panel(
            f"[bold]{issue.id}[/bold] - {issue.severity}\n"
            f"[dim]{issue.file}:{issue.line}[/dim]",
            title="Explicando Issue",
            border_style="cyan",
        )
    )

    # Get code context
    code_context = get_code_context(issue.file, issue.line)

    console.print("\n[dim]Código:[/dim]")
    console.print(Panel(code_context, border_style="dim"))

    # Get AI explanation
    console.print("\n[dim]Consultando AI...[/dim]")

    try:
        ai_client = _get_ai_client()
        issue_dict = {
            "id": issue.id,
            "tool": issue.tool,
            "rule": issue.rule,
            "severity": issue.severity,
            "file": issue.file,
            "line": issue.line,
            "message": issue.message,
        }
        explanation = ai_client.explain_issue(issue_dict, code_context)

        console.print()
        console.print(Markdown(explanation))

    except ValueError as e:
        console.print(f"\n[red]Error:[/red] {e}")
        console.print(
            "[dim]Configura ANTHROPIC_API_KEY en .env para usar esta función.[/dim]"
        )
    except Exception as e:
        console.print(f"\n[red]Error al consultar AI:[/red] {e}")


def fix_issue(issue_id: str) -> None:
    """Fix a security issue using AI."""
    global _issues_by_id, _last_scan

    if not _issues_by_id:
        console.print("[yellow]No hay scan reciente. Usa 'analiza' primero.[/yellow]")
        return

    # Find the issue
    issue = _issues_by_id.get(issue_id)
    if not issue:
        console.print(f"[red]Issue '{issue_id}' no encontrado.[/red]")
        console.print("[dim]Usa 'issues' para ver la lista de issues.[/dim]")
        return

    console.print()
    console.print(
        Panel(
            f"[bold]{issue.id}[/bold] - {issue.severity}\n"
            f"[dim]{issue.file}:{issue.line}[/dim]",
            title="Aplicando Fix",
            border_style="yellow",
        )
    )

    # Get the line content that needs fixing
    old_code = get_line_content(issue.file, issue.line)
    if not old_code:
        console.print("[red]No se pudo leer el archivo.[/red]")
        return

    # Get code context for AI
    code_context = get_code_context(issue.file, issue.line)

    console.print("\n[dim]Código actual:[/dim]")
    console.print(Panel(code_context, border_style="red"))

    # Generate fix with AI
    console.print("\n[dim]Generando fix con AI...[/dim]")

    try:
        ai_client = _get_ai_client()
        issue_dict = {
            "id": issue.id,
            "tool": issue.tool,
            "rule": issue.rule,
            "severity": issue.severity,
            "file": issue.file,
            "line": issue.line,
            "message": issue.message,
        }
        new_code = ai_client.generate_fix(issue_dict, code_context)

        if not new_code:
            console.print("[red]No se pudo generar un fix.[/red]")
            return

        console.print("\n[dim]Código sugerido:[/dim]")
        console.print(Panel(new_code, border_style="green"))

        # Ask for confirmation
        confirm = console.input("\n[bold]¿Aplicar este fix? (s/n):[/bold] ").strip()

        if confirm.lower() in ("s", "si", "sí", "y", "yes"):
            # Apply the fix
            success, error = apply_fix(issue.file, old_code, new_code)
            if success:
                console.print("\n[green]✓ Fix aplicado correctamente.[/green]")

                # Re-scan to validate
                console.print("[dim]Re-escaneando para validar...[/dim]")
                asyncio.run(run_scan())

                # Check if issue is resolved
                if issue_id not in _issues_by_id:
                    console.print(f"[green]✓ {issue_id} resuelto![/green]")
                else:
                    console.print(
                        f"[yellow]⚠ {issue_id} todavía presente. El fix puede necesitar ajustes.[/yellow]"
                    )
            else:
                console.print(f"[red]No se pudo aplicar el fix:[/red] {error}")
        else:
            console.print("[dim]Fix cancelado.[/dim]")

    except ValueError as e:
        console.print(f"\n[red]Error:[/red] {e}")
        console.print(
            "[dim]Configura ANTHROPIC_API_KEY en .env para usar esta función.[/dim]"
        )
    except Exception as e:
        console.print(f"\n[red]Error al generar fix:[/red] {e}")


def show_help() -> None:
    """Show available commands."""
    help_text = """
[bold]Comandos disponibles:[/bold]

  [cyan]analiza[/cyan] / [cyan]scan[/cyan]      Escanea el proyecto
  [cyan]analiza <path>[/cyan]     Escanea archivo o carpeta específica
  [cyan]score[/cyan]              Muestra Production-Ready Score
  [cyan]issues[/cyan] / [cyan]lista[/cyan]     Lista todos los issues
  [cyan]explica <ID>[/cyan]       Explica un issue con AI
  [cyan]fix <ID>[/cyan]           Genera y aplica fix con AI
  [cyan]ayuda[/cyan] / [cyan]help[/cyan]       Muestra esta ayuda
  [cyan]salir[/cyan] / [cyan]exit[/cyan]       Sale del chat

[bold]También puedes preguntar en español:[/bold]
  > ¿qué problemas tiene mi código?
  > ¿está seguro mi proyecto?
  > analiza solo src/db.py
  > ¿cómo arreglo el sql injection?
  > arregla el SEC-e2675564
  > muestra los issues

[bold]Ejemplos de comandos:[/bold]
  > explica SEC-e2675564
  > fix SEC-e2675564
"""
    console.print(help_text)
