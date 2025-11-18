#!/usr/bin/env python3
"""Pneumonia ontology example for ADORE demonstration.

This script creates a sample Pneumonia ontology and runs the ADORE workflow.
"""

from pathlib import Path
from adore.core.models import WorkflowState
from adore.infrastructure.config import get_settings
from adore.infrastructure.logging import configure_logging, get_logger
from adore.services.llm_service import LLMService
from adore.services.ontology_service import OntologyService
from adore.services.workflow_service import WorkflowOrchestrator

# Initialize
configure_logging()
logger = get_logger(__name__)
settings = get_settings()


def create_pneumonia_ontology() -> Path:
    """Create a sample Pneumonia ontology.

    Returns:
        Path: Path to the created ontology file.
    """
    from owlready2 import Thing, ObjectProperty, get_ontology

    logger.info("Creating Pneumonia ontology")

    # Create ontology
    onto = get_ontology("http://example.org/pneumonia.owl")

    with onto:
        # Define classes
        class Pneumonia(Thing):
            pass

        class Bacterium(Thing):
            pass

        class NovelVirusX(Thing):
            pass

        class Pathogen(Thing):
            pass

        # Define properties
        class causedBy(ObjectProperty):
            domain = [Pneumonia]
            range = [Thing]

        # Add axioms
        Pneumonia.is_a.append(causedBy.some(Bacterium))
        Bacterium.disjoint_with = [NovelVirusX]
        Pneumonia.is_a.append(causedBy.max(1, Thing))

    # Save ontology
    output_path = settings.ontology_cache_dir / "pneumonia.owl"
    onto.save(file=str(output_path), format="rdfxml")

    logger.info("Pneumonia ontology created", path=str(output_path))
    return output_path


def main() -> None:
    """Run the Pneumonia example."""
    print("=" * 70)
    print("  ADORE Pneumonia Ontology Example")
    print("=" * 70)
    print()

    # Create ontology
    ontology_path = create_pneumonia_ontology()
    print(f"✓ Created ontology: {ontology_path}")
    print()

    # Initialize services
    llm_service = LLMService()
    ontology_service = OntologyService()
    orchestrator = WorkflowOrchestrator(llm_service, ontology_service, auto_hitl=True)

    print("✓ Services initialized")
    print()

    # Run a single ADORE cycle
    print("Running ADORE cycle...")
    print("-" * 70)

    initial_state = WorkflowState(cycle_id=1, ontology_path=ontology_path)

    final_state = orchestrator.run_cycle(initial_state)

    print("-" * 70)
    print()

    # Display results
    print("Results:")
    print(f"  Proposed Axiom: {final_state.candidate_axiom.content if final_state.candidate_axiom else 'None'}")
    print(f"  Consistent: {final_state.is_consistent}")
    print(f"  Strategy: {final_state.chosen_strategy.value if final_state.chosen_strategy else 'None'}")
    print(f"  Repairs: {len(final_state.repair_proposals)}")
    print()

    print("=" * 70)
    print("  Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
