"""Consistency Guard Agent for checking ontology consistency."""

from pathlib import Path

from adore.agents.base import BaseAgent
from adore.core.constants import AgentType
from adore.core.exceptions import AgentException
from adore.core.models import WorkflowState
from adore.services.ontology_service import OntologyService


class ConsistencyGuardAgent(BaseAgent):
    """Agent that checks if adding a candidate axiom maintains consistency.

    This agent creates a temporary ontology copy, adds the candidate axiom,
    and runs the reasoner to check for logical inconsistencies.
    """

    def __init__(self, ontology_service: OntologyService) -> None:
        """Initialize the Consistency Guard Agent.

        Args:
            ontology_service: Service for ontology operations.
        """
        super().__init__(AgentType.CONSISTENCY_GUARD)
        self.ontology_service = ontology_service

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Check consistency of ontology with candidate axiom.

        Args:
            state: Current workflow state.

        Returns:
            WorkflowState: Updated state with is_consistent field.

        Raises:
            AgentException: If consistency check fails.
        """
        try:
            self.logger.info("Starting consistency check", cycle_id=state.cycle_id)

            if not state.candidate_axiom:
                raise AgentException("No candidate axiom to check")

            if not state.ontology_path:
                raise AgentException("No ontology path provided")

            # Load original ontology
            original_ontology = self.ontology_service.load_ontology(state.ontology_path)

            # Duplicate for testing
            temp_ontology, temp_path = self.ontology_service.duplicate_ontology(original_ontology)

            try:
                # Add candidate axiom to temp ontology
                self.ontology_service.add_axiom_from_string(
                    state.candidate_axiom.content, temp_ontology
                )

                # Check consistency
                is_consistent = self.ontology_service.check_consistency(temp_ontology)

                state.is_consistent = is_consistent

                if is_consistent:
                    self.log_action(state, "consistency_check_passed", {"axiom": state.candidate_axiom.content})
                    self.logger.info("Axiom is consistent with ontology")
                else:
                    # Extract inconsistent axioms
                    axioms = self.ontology_service.extract_axioms(temp_ontology)
                    state.inconsistent_axioms = axioms
                    self.log_action(
                        state,
                        "inconsistency_detected",
                        {
                            "axiom": state.candidate_axiom.content,
                            "num_conflicts": len(axioms),
                        },
                    )
                    self.logger.warning("Axiom creates inconsistency", num_axioms=len(axioms))

                return state

            finally:
                # Cleanup temp file
                if temp_path.exists():
                    temp_path.unlink()

        except Exception as e:
            self.logger.error("Consistency check failed", error=str(e))
            self.log_action(state, "consistency_check_error", {"error": str(e)})
            state.is_consistent = False
            raise AgentException(f"Consistency Guard failed: {e}") from e
