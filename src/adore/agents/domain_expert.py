"""Domain Expert Agent for assessing axiom plausibility."""

from adore.agents.base import BaseAgent
from adore.core.constants import AgentType
from adore.core.exceptions import AgentException
from adore.core.models import Assessment, WorkflowState
from adore.services.llm_service import LLMService


class DomainExpertAgent(BaseAgent):
    """Agent that assesses the domain plausibility of proposed axioms.

    This agent evaluates whether a proposed axiom makes sense from a
    domain knowledge perspective (e.g., medical, scientific correctness).
    """

    def __init__(self, llm_service: LLMService) -> None:
        """Initialize the Domain Expert Agent.

        Args:
            llm_service: Service for LLM-based assessment.
        """
        super().__init__(AgentType.DOMAIN_EXPERT)
        self.llm_service = llm_service

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Assess the domain plausibility of the candidate axiom.

        Args:
            state: Current workflow state with candidate_axiom.

        Returns:
            WorkflowState: Updated state with dea_assessment.

        Raises:
            AgentException: If assessment fails.
        """
        try:
            self.logger.info("Starting domain expert assessment", cycle_id=state.cycle_id)

            if not state.candidate_axiom:
                raise AgentException("No candidate axiom to assess")

            axiom_str = state.candidate_axiom.content

            # Use LLM for sophisticated assessment or simple heuristic
            try:
                result = self.llm_service.assess_axiom(
                    axiom=axiom_str,
                    assessment_type="domain expert",
                    criteria=(
                        "Evaluate whether this axiom is plausible and correct from a "
                        "domain knowledge perspective. Consider semantic validity."
                    ),
                )

                assessment = Assessment(
                    score=min(1.0, max(0.0, float(result.get("score", 0.5)))),
                    justification=result.get("justification", "LLM-based assessment"),
                    metadata={"method": "llm_assessment"},
                )

            except Exception:
                # Fallback to simple heuristic
                self.logger.warning("LLM assessment failed, using heuristic")
                score = 0.7 if len(axiom_str) > 10 else 0.3
                assessment = Assessment(
                    score=score,
                    justification="Heuristic-based assessment (LLM unavailable)",
                    metadata={"method": "heuristic"},
                )

            state.dea_assessment = assessment
            self.log_action(
                state,
                "assessment_completed",
                {"score": assessment.score, "justification": assessment.justification},
            )

            self.logger.info("Domain assessment completed", score=assessment.score)
            return state

        except Exception as e:
            self.logger.error("Domain assessment failed", error=str(e))
            self.log_action(state, "assessment_failed", {"error": str(e)})
            raise AgentException(f"Domain Expert assessment failed: {e}") from e
