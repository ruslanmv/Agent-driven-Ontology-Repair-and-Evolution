"""Meta-Knowledge Agent for logging and knowledge consolidation."""

import json
from datetime import datetime
from pathlib import Path

from adore.agents.base import BaseAgent
from adore.core.constants import AgentType, WorkflowStrategy
from adore.core.exceptions import AgentException
from adore.core.models import CycleReport, WorkflowState
from adore.infrastructure.config import get_settings
from adore.infrastructure.logging import log_to_file
from adore.services.ontology_service import OntologyService


class MetaKnowledgeAgent(BaseAgent):
    """Agent responsible for logging and consolidating knowledge.

    This agent finalizes the workflow by:
    1. Logging all decisions and actions
    2. Updating the active ontology
    3. Generating a cycle report
    """

    def __init__(self, ontology_service: OntologyService) -> None:
        """Initialize the Meta-Knowledge Agent.

        Args:
            ontology_service: Service for ontology operations.
        """
        super().__init__(AgentType.META_KNOWLEDGE)
        self.ontology_service = ontology_service

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Consolidate knowledge and generate cycle report.

        Args:
            state: Current workflow state.

        Returns:
            WorkflowState: Final updated state with report.

        Raises:
            AgentException: If consolidation fails.
        """
        try:
            self.logger.info("Starting knowledge consolidation", cycle_id=state.cycle_id)
            start_time = datetime.now()

            # Determine final ontology
            final_ontology_path = state.final_ontology_path or state.ontology_path

            # Extract final axioms
            if final_ontology_path:
                try:
                    final_ontology = self.ontology_service.load_ontology(final_ontology_path)
                    final_axioms = self.ontology_service.extract_axioms(final_ontology)
                except Exception as e:
                    self.logger.warning("Could not extract final axioms", error=str(e))
                    final_axioms = []
            else:
                final_axioms = []

            # Create cycle report
            report = CycleReport(
                cycle_id=state.cycle_id,
                candidate_axiom=state.candidate_axiom.content if state.candidate_axiom else None,
                assessments={
                    "domain_expert": state.dea_assessment
                    if state.dea_assessment
                    else None,
                    "linguistic_insight": state.lia_assessment
                    if state.lia_assessment
                    else None,
                },
                consistency_result=state.is_consistent,
                strategy=state.chosen_strategy,
                repair_applied=len(state.repair_proposals) > 0,
                final_axioms=final_axioms[:20],  # Limit to avoid huge logs
                execution_time_seconds=(datetime.now() - start_time).total_seconds(),
            )

            # Save report to file
            settings = get_settings()
            report_path = settings.log_dir / f"cycle_{state.cycle_id}_report.json"
            log_to_file(report_path, report.model_dump(mode="json"))

            # Log summary
            self.log_action(
                state,
                "cycle_completed",
                {
                    "strategy": state.chosen_strategy.value if state.chosen_strategy else None,
                    "repair_applied": report.repair_applied,
                    "final_axiom_count": len(final_axioms),
                    "report_path": str(report_path),
                },
            )

            self.logger.info(
                "Cycle completed",
                strategy=state.chosen_strategy.value if state.chosen_strategy else None,
                execution_time=report.execution_time_seconds,
            )

            # Store report in metadata
            state.metadata["cycle_report"] = report.model_dump()

            return state

        except Exception as e:
            self.logger.error("Meta-knowledge consolidation failed", error=str(e))
            raise AgentException(f"Meta-Knowledge Agent failed: {e}") from e
