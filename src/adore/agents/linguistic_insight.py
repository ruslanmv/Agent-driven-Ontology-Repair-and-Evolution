"""Linguistic Insight Agent for assessing axiom syntax."""

from adore.agents.base import BaseAgent
from adore.core.constants import AgentType
from adore.core.exceptions import AgentException
from adore.core.models import Assessment, WorkflowState


class LinguisticInsightAgent(BaseAgent):
    """Agent that assesses the linguistic and syntactic correctness of axioms.

    This agent verifies that proposed axioms are well-formed according to
    Description Logic syntax rules.
    """

    def __init__(self) -> None:
        """Initialize the Linguistic Insight Agent."""
        super().__init__(AgentType.LINGUISTIC_INSIGHT)

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Assess the syntactic correctness of the candidate axiom.

        Args:
            state: Current workflow state with candidate_axiom.

        Returns:
            WorkflowState: Updated state with lia_assessment.

        Raises:
            AgentException: If assessment fails.
        """
        try:
            self.logger.info("Starting linguistic assessment", cycle_id=state.cycle_id)

            if not state.candidate_axiom:
                raise AgentException("No candidate axiom to assess")

            axiom_str = state.candidate_axiom.content

            # Check for basic DL syntax patterns
            score = 0.0
            justification_parts = []

            # Check for subsumption symbol
            if "⊑" in axiom_str:
                score += 0.3
                justification_parts.append("contains subsumption symbol")
            else:
                justification_parts.append("missing subsumption symbol")

            # Check for existential restriction
            if "∃" in axiom_str:
                score += 0.3
                justification_parts.append("contains existential quantifier")

            # Check for property separator
            if "." in axiom_str:
                score += 0.2
                justification_parts.append("has property.filler structure")

            # Check minimum length
            if len(axiom_str) > 5:
                score += 0.2
                justification_parts.append("sufficient length")

            score = min(1.0, score)  # Cap at 1.0
            justification = "Syntactic analysis: " + ", ".join(justification_parts)

            assessment = Assessment(
                score=score, justification=justification, metadata={"axiom_length": len(axiom_str)}
            )

            state.lia_assessment = assessment
            self.log_action(
                state,
                "assessment_completed",
                {"score": assessment.score, "justification": assessment.justification},
            )

            self.logger.info("Linguistic assessment completed", score=assessment.score)
            return state

        except Exception as e:
            self.logger.error("Linguistic assessment failed", error=str(e))
            self.log_action(state, "assessment_failed", {"error": str(e)})
            raise AgentException(f"Linguistic Insight assessment failed: {e}") from e
