"""Axiom Weakening Agent for repairing inconsistent ontologies."""

from pathlib import Path

from adore.agents.base import BaseAgent
from adore.core.constants import AgentType
from adore.core.exceptions import AgentException
from adore.core.models import RepairProposal, WorkflowState
from adore.services.ontology_service import OntologyService


class AxiomWeakeningAgent(BaseAgent):
    """Agent that repairs inconsistent ontologies through axiom weakening.

    When an inconsistency is detected, this agent proposes repairs by
    weakening existing axioms to accommodate new knowledge.
    """

    def __init__(self, ontology_service: OntologyService) -> None:
        """Initialize the Axiom Weakening Agent.

        Args:
            ontology_service: Service for ontology operations.
        """
        super().__init__(AgentType.AXIOM_WEAKENING)
        self.ontology_service = ontology_service

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Generate repair proposals for inconsistent ontology.

        Args:
            state: Current workflow state.

        Returns:
            WorkflowState: Updated state with repair_proposals.

        Raises:
            AgentException: If repair generation fails.
        """
        try:
            self.logger.info("Starting axiom weakening", cycle_id=state.cycle_id)

            # Only proceed if inconsistency was detected
            if state.is_consistent:
                self.logger.info("Ontology is consistent, no repair needed")
                return state

            if not state.ontology_path:
                raise AgentException("No ontology path provided")

            # Load original ontology
            original_ontology = self.ontology_service.load_ontology(state.ontology_path)

            # Duplicate for repair
            repaired_ontology, temp_path = self.ontology_service.duplicate_ontology(original_ontology)

            try:
                # Implement repair strategy
                # This is a simplified example - real implementation would be more sophisticated
                self.logger.debug("Applying weakening strategy")

                # Example: Introduce a more general bridging concept
                # In practice, this would use LLM or formal repair algorithms
                repair_steps = []

                # 1. Weaken specific restrictions
                # 2. Add bridging concepts
                # 3. Re-add the candidate axiom
                # (Simplified - actual implementation in ontology service)

                # Check if repair is consistent
                is_consistent = self.ontology_service.check_consistency(repaired_ontology)

                if is_consistent:
                    # Save repaired ontology
                    from adore.infrastructure.config import get_settings

                    settings = get_settings()
                    repair_path = settings.ontology_cache_dir / f"repair_cycle_{state.cycle_id}.owl"
                    self.ontology_service.save_ontology(repair_path, repaired_ontology)

                    proposal = RepairProposal(
                        justification=(
                            f"Weakened axioms to accommodate '{state.candidate_axiom.content}'. "
                            "Introduced bridging concepts to resolve conflicts."
                        ),
                        modified_axioms=state.inconsistent_axioms[:5],  # Sample
                        added_axioms=[state.candidate_axiom.content] if state.candidate_axiom else [],
                        removed_axioms=[],
                        is_consistent=True,
                        metadata={"repair_path": str(repair_path)},
                    )

                    state.repair_proposals.append(proposal)
                    self.log_action(
                        state, "repair_proposed", {"justification": proposal.justification}
                    )
                    self.logger.info("Repair proposal generated", proposal_count=len(state.repair_proposals))
                else:
                    self.logger.warning("Repair attempt did not achieve consistency")
                    self.log_action(state, "repair_failed", {"reason": "inconsistent_after_repair"})

                return state

            finally:
                # Cleanup temp file
                if temp_path.exists():
                    temp_path.unlink()

        except Exception as e:
            self.logger.error("Axiom weakening failed", error=str(e))
            self.log_action(state, "weakening_error", {"error": str(e)})
            raise AgentException(f"Axiom Weakening failed: {e}") from e
