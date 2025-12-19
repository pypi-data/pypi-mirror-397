"""QodaBit CLI - Main entry point."""

import asyncio
import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from qodabit import __version__
from qodabit.config.loader import create_default_config, load_config
from qodabit.scanner.orchestrator import count_by_severity, scan_project
from qodabit.score.calculator import calculate_score
from qodabit.score.gates import evaluate_gates

# Exit codes
EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_ERROR = 2

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="qodabit")
@click.pass_context
def main(ctx: click.Context) -> None:
    """QodaBit - Security Copilot for AI Devs."""
    if ctx.invoked_subcommand is None:
        # Sin comando = modo chat
        from qodabit.chat.engine import start_chat

        start_chat()


@main.command()
@click.option("--path", "-p", default=".", help="Path to scan")
def check(path: str) -> None:
    """Scan project and evaluate gates. Returns exit code 0 (pass) or 1 (fail)."""
    try:
        result = asyncio.run(scan_project(path))
        config = load_config(path)

        # Calculate score
        issues_dicts = [{"severity": i.severity, "tool": i.tool} for i in result.issues]
        score_result = calculate_score(issues_dicts)

        # Get gate config (default to 'pr' gate)
        gate_config = config.get("gates", {}).get(
            "pr",
            {
                "critical": 0,
                "high": 0,
                "secrets": 0,
                "score_min": 80,
            },
        )

        # Evaluate gates
        gate_result = evaluate_gates(issues_dicts, score_result.score, gate_config)

        # Show results
        _show_scan_summary(result, score_result)
        _show_gate_result(gate_result)

        # Exit with appropriate code
        sys.exit(EXIT_PASS if gate_result.passed else EXIT_FAIL)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(EXIT_ERROR)


@main.command()
@click.option("--path", "-p", default=".", help="Path to scan")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--gate", type=str, help="Gate to evaluate (e.g., 'pr')")
def audit(path: str, output_json: bool, gate: Optional[str]) -> None:
    """Scan project and show results."""
    try:
        result = asyncio.run(scan_project(path))
        config = load_config(path)

        # Calculate score
        issues_dicts = [{"severity": i.severity, "tool": i.tool} for i in result.issues]
        score_result = calculate_score(issues_dicts)

        # Evaluate gates if requested
        gate_result = None
        if gate:
            gate_config = config.get("gates", {}).get(gate, {})
            if not gate_config:
                console.print(
                    f"[yellow]Warning: Gate '{gate}' not found in config[/yellow]"
                )
            else:
                gate_result = evaluate_gates(
                    issues_dicts, score_result.score, gate_config
                )

        if output_json:
            # JSON output for CI
            output = _build_json_output(result, score_result, gate_result)
            click.echo(json.dumps(output, indent=2))
        else:
            # Human-readable output
            _show_scan_summary(result, score_result)
            if gate_result:
                _show_gate_result(gate_result)

        # Exit code based on gates (if evaluated)
        if gate_result:
            sys.exit(EXIT_PASS if gate_result.passed else EXIT_FAIL)

    except Exception as e:
        if output_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        sys.exit(EXIT_ERROR)


@main.command()
@click.option("--path", "-p", default=".", help="Path to scan")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def score(path: str, output_json: bool) -> None:
    """Show Production-Ready Score."""
    try:
        result = asyncio.run(scan_project(path))

        # Calculate score
        issues_dicts = [{"severity": i.severity} for i in result.issues]
        score_result = calculate_score(issues_dicts)

        if output_json:
            click.echo(
                json.dumps(
                    {
                        "score": score_result.score,
                        "category": score_result.category,
                    }
                )
            )
        else:
            _show_score_panel(score_result)

    except Exception as e:
        if output_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        sys.exit(EXIT_ERROR)


@main.command()
@click.option("--path", "-p", default=".", help="Path to create config")
def init(path: str) -> None:
    """Create qodabit.yaml config file."""
    try:
        from pathlib import Path

        config_path = Path(path) / "qodabit.yaml"

        if config_path.exists():
            console.print(
                f"[yellow]qodabit.yaml already exists at {config_path}[/yellow]"
            )
            return

        create_default_config(path)
        console.print(f"[green]✓[/green] Created qodabit.yaml at {config_path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(EXIT_ERROR)


def _show_scan_summary(result, score_result) -> None:
    """Show scan summary with Rich formatting."""
    # Show tools run
    console.print()
    for tool in result.tools_run:
        console.print(f"[green]✓[/green] {tool}")

    if result.errors:
        for error in result.errors:
            console.print(f"[yellow]⚠[/yellow] {error}")

    console.print(f"[dim]Tiempo: {result.duration_ms}ms[/dim]")

    # Show score
    _show_score_panel(score_result)

    # Show issues by severity
    if result.issues:
        counts = count_by_severity(result.issues)
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

            for issue in result.issues:
                if issue.severity == severity:
                    console.print(
                        f"   [{config['color']}]{issue.id}[/{config['color']}]  {issue.message[:40]:<40}  [dim]{issue.file}:{issue.line}[/dim]"
                    )
    else:
        console.print("\n[green]✓ No se encontraron issues de seguridad[/green]")


def _show_score_panel(score_result) -> None:
    """Show score in a Rich panel."""
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


def _show_gate_result(gate_result) -> None:
    """Show gate evaluation result."""
    console.print()
    if gate_result.passed:
        console.print("[green]Gates: PASS[/green]")
    else:
        console.print("[red]Gates: FAIL[/red]")

    for gate_name, details in gate_result.details.items():
        status = "[green]✓[/green]" if details["passed"] else "[red]✗[/red]"
        console.print(
            f"  {status} {gate_name}: {details['actual']} (threshold: {details['threshold']})"
        )


def _build_json_output(result, score_result, gate_result=None) -> dict:
    """Build JSON output for CI."""
    output = {
        "score": score_result.score,
        "category": score_result.category,
        "summary": count_by_severity(result.issues),
        "issues": [
            {
                "id": issue.id,
                "tool": issue.tool,
                "rule": issue.rule,
                "severity": issue.severity,
                "file": issue.file,
                "line": issue.line,
                "message": issue.message,
            }
            for issue in result.issues
        ],
        "duration_ms": result.duration_ms,
    }

    if gate_result:
        output["gates"] = {
            "status": "PASS" if gate_result.passed else "FAIL",
            "failed": gate_result.failed_gates,
            "details": gate_result.details,
        }

    return output


if __name__ == "__main__":
    main()
