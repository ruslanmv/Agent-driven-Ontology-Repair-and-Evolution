"""CLI commands for ADORE using Typer and Rich.

This module provides a beautiful command-line interface for interacting
with the ADORE framework.
"""

from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from adore.core.constants import ADORE_BANNER
from adore.core.models import WorkflowState
from adore.infrastructure.config import get_settings
from adore.infrastructure.logging import configure_logging, get_logger
from adore.services.llm_service import LLMService
from adore.services.ontology_service import OntologyService
from adore.services.workflow_service import WorkflowOrchestrator

app = typer.Typer(
    name="adore",
    help="🧠 ADORE - Agent-Driven Ontology Repair and Evolution",
    add_completion=False,
)

console = Console()


def show_banner() -> None:
    """Display the ADORE banner."""
    settings = get_settings()
    if settings.show_banner:
        console.print(ADORE_BANNER, style="bold blue")


@app.command()
def run(
    ontology_path: Path = typer.Option(
        ...,
        "--ontology",
        "-o",
        exists=True,
        help="Path to the ontology file (OWL format)",
    ),
    cycles: int = typer.Option(
        1,
        "--cycles",
        "-c",
        min=1,
        max=10,
        help="Number of ADORE cycles to run",
    ),
    auto_hitl: bool = typer.Option(
        True,
        "--auto-hitl",
        help="Run HITL stages in automatic mode",
    ),
    json_logs: bool = typer.Option(
        False,
        "--json-logs",
        help="Enable JSON logging output",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
) -> None:
    """Run ADORE ontology evolution cycles.

    This command executes one or more cycles of the ADORE workflow,
    processing the specified ontology and proposing/applying repairs.
    """
    # Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(json_output=json_logs, log_level=log_level)
    logger = get_logger(__name__)

    show_banner()

    try:
        # Display configuration
        console.print("\n[bold cyan]Configuration:[/bold cyan]")
        config_table = Table(show_header=False, box=box.SIMPLE)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="yellow")
        config_table.add_row("Ontology", str(ontology_path))
        config_table.add_row("Cycles", str(cycles))
        config_table.add_row("Auto HITL", "✓" if auto_hitl else "✗")
        config_table.add_row("JSON Logs", "✓" if json_logs else "✗")
        console.print(config_table)
        console.print()

        # Initialize services
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing ADORE...", total=None)

            llm_service = LLMService()
            ontology_service = OntologyService()
            orchestrator = WorkflowOrchestrator(llm_service, ontology_service, auto_hitl=auto_hitl)

            progress.update(task, description="[green]✓ Initialization complete")

        # Run cycles
        for cycle_num in range(1, cycles + 1):
            console.print(f"\n[bold magenta]{'='*60}[/bold magenta]")
            console.print(f"[bold magenta]  ADORE Cycle {cycle_num}/{cycles}[/bold magenta]")
            console.print(f"[bold magenta]{'='*60}[/bold magenta]\n")

            # Create initial state
            initial_state = WorkflowState(
                cycle_id=cycle_num,
                ontology_path=ontology_path,
            )

            # Run cycle with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Running cycle {cycle_num}...", total=None)

                final_state = orchestrator.run_cycle(initial_state)

                progress.update(task, description=f"[green]✓ Cycle {cycle_num} complete")

            # Display results
            _display_cycle_results(final_state, console)

            # Update ontology path for next cycle if repair was applied
            if final_state.final_ontology_path:
                ontology_path = final_state.final_ontology_path

        # Final summary
        console.print("\n[bold green]{'='*60}[/bold green]")
        console.print("[bold green]  All cycles completed successfully! 🎉[/bold green]")
        console.print("[bold green]{'='*60}[/bold green]\n")

    except Exception as e:
        logger.error("ADORE execution failed", error=str(e))
        console.print(f"\n[bold red]Error:[/bold red] {e}\n", style="red")
        raise typer.Exit(code=1)


@app.command()
def validate(
    ontology_path: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to the ontology file to validate",
    ),
) -> None:
    """Validate an ontology file for consistency.

    Checks if the ontology is logically consistent using a DL reasoner.
    """
    show_banner()

    console.print(f"\n[cyan]Validating ontology:[/cyan] {ontology_path}\n")

    try:
        ontology_service = OntologyService()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading ontology...", total=None)

            ontology = ontology_service.load_ontology(ontology_path)
            progress.update(task, description="Checking consistency...")

            is_consistent = ontology_service.check_consistency(ontology)

        if is_consistent:
            console.print(Panel(
                "[bold green]✓ Ontology is consistent[/bold green]",
                title="Validation Result",
                border_style="green",
            ))
        else:
            console.print(Panel(
                "[bold red]✗ Ontology is inconsistent[/bold red]",
                title="Validation Result",
                border_style="red",
            ))

        # Display axioms
        axioms = ontology_service.extract_axioms(ontology)
        console.print(f"\n[cyan]Total axioms:[/cyan] {len(axioms)}\n")

        if axioms:
            table = Table(title="Ontology Axioms", box=box.ROUNDED)
            table.add_column("#", style="dim", width=6)
            table.add_column("Axiom", style="cyan")

            for i, axiom in enumerate(axioms[:20], 1):
                table.add_row(str(i), axiom)

            if len(axioms) > 20:
                table.add_row("...", f"[dim]({len(axioms) - 20} more axioms)[/dim]")

            console.print(table)
            console.print()

    except Exception as e:
        console.print(f"\n[bold red]Validation failed:[/bold red] {e}\n")
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Display ADORE version information."""
    show_banner()

    version_info = Table(show_header=False, box=box.DOUBLE)
    version_info.add_column("Field", style="cyan bold")
    version_info.add_column("Value", style="yellow")

    version_info.add_row("Version", "1.0.0")
    version_info.add_row("Authors", "Ruslan Magana, Marco Monti")
    version_info.add_row("License", "Apache 2.0")
    version_info.add_row("GitHub", "github.com/ruslanmv/Agent-driven-Ontology-Repair-and-Evolution")

    console.print(version_info)
    console.print()


def _display_cycle_results(state: WorkflowState, console: Console) -> None:
    """Display results of a workflow cycle.

    Args:
        state: Final workflow state.
        console: Rich console for output.
    """
    # Results table
    results = Table(title="Cycle Results", box=box.ROUNDED, show_header=True)
    results.add_column("Metric", style="cyan bold")
    results.add_column("Value", style="yellow")

    if state.candidate_axiom:
        results.add_row("Proposed Axiom", state.candidate_axiom.content)

    if state.dea_assessment:
        results.add_row(
            "Domain Assessment",
            f"{state.dea_assessment.score:.2f} - {state.dea_assessment.justification[:50]}...",
        )

    if state.lia_assessment:
        results.add_row(
            "Linguistic Assessment",
            f"{state.lia_assessment.score:.2f} - {state.lia_assessment.justification[:50]}...",
        )

    results.add_row("Consistent", "✓" if state.is_consistent else "✗")

    if state.chosen_strategy:
        results.add_row("Strategy", state.chosen_strategy.value)

    results.add_row("Repairs Applied", str(len(state.repair_proposals)))

    console.print(results)
    console.print()
