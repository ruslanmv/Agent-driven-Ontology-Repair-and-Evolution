"""Human-in-the-Loop agents for decision making."""

from adore.agents.base import BaseAgent
from adore.core.constants import AgentType, WorkflowStrategy
from adore.core.exceptions import AgentException
from adore.core.models import WorkflowState


class HITLStage1Agent(BaseAgent):
    """First Human-in-the-Loop decision point.

    Decides whether to accept the axiom or initiate ontology evolution (repair).
    """

    def __init__(self, auto_mode: bool = True) -> None:
        """Initialize HITL Stage 1 Agent.

        Args:
            auto_mode: If True, automatically decide based on consistency.
                      If False, would prompt for human input (CLI mode).
        """
        super().__init__(AgentType.HITL_STAGE1)
        self.auto_mode = auto_mode

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Make strategic decision based on consistency check.

        Args:
            state: Current workflow state.

        Returns:
            WorkflowState: Updated state with chosen_strategy.

        Raises:
            AgentException: If decision fails.
        """
        try:
            self.logger.info("HITL Stage 1: Making strategic decision", cycle_id=state.cycle_id)

            if self.auto_mode:
                # Automatic decision based on consistency
                if state.is_consistent:
                    strategy = WorkflowStrategy.ACCEPT_AXIOM
                    rationale = "Axiom is consistent with current ontology - accepting"
                else:
                    strategy = WorkflowStrategy.ONTOLOGY_EVOLUTION
                    rationale = "Inconsistency detected - initiating repair process"
            else:
                # In non-auto mode, this would prompt user
                # For now, fallback to auto behavior
                strategy = (
                    WorkflowStrategy.ACCEPT_AXIOM
                    if state.is_consistent
                    else WorkflowStrategy.ONTOLOGY_EVOLUTION
                )
                rationale = "Auto-decision (interactive mode not implemented)"

            state.chosen_strategy = strategy
            self.log_action(state, "strategy_chosen", {"strategy": strategy.value, "rationale": rationale})

            self.logger.info("Strategy chosen", strategy=strategy.value)
            return state

        except Exception as e:
            self.logger.error("HITL Stage 1 failed", error=str(e))
            raise AgentException(f"HITL Stage 1 failed: {e}") from e


class HITLStage2Agent(BaseAgent):
    """Second Human-in-the-Loop decision point.

    Reviews and approves repair proposals.
    """

    def __init__(self, auto_mode: bool = True) -> None:
        """Initialize HITL Stage 2 Agent.

        Args:
            auto_mode: If True, automatically accept first valid proposal.
        """
        super().__init__(AgentType.HITL_STAGE2)
        self.auto_mode = auto_mode

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Review and select repair proposal.

        Args:
            state: Current workflow state with repair_proposals.

        Returns:
            WorkflowState: Updated state with approved repair.

        Raises:
            AgentException: If decision fails.
        """
        try:
            self.logger.info("HITL Stage 2: Reviewing repair proposals", cycle_id=state.cycle_id)

            if not state.repair_proposals:
                self.logger.warning("No repair proposals to review")
                self.log_action(state, "no_proposals", {})
                return state

            if self.auto_mode:
                # Automatically accept first consistent proposal
                for i, proposal in enumerate(state.repair_proposals):
                    if proposal.is_consistent:
                        self.log_action(
                            state,
                            "proposal_accepted",
                            {"proposal_index": i, "justification": proposal.justification},
                        )
                        self.logger.info("Repair proposal accepted", index=i)

                        # Update ontology path if repair was saved
                        if "repair_path" in proposal.metadata:
                            from pathlib import Path

                            state.final_ontology_path = Path(proposal.metadata["repair_path"])

                        return state

                self.logger.warning("No consistent proposals found")
                self.log_action(state, "no_consistent_proposals", {})
            else:
                # In non-auto mode, would prompt user to select
                # For now, fallback to auto behavior
                self.logger.warning("Interactive mode not implemented, using auto mode")

            return state

        except Exception as e:
            self.logger.error("HITL Stage 2 failed", error=str(e))
            raise AgentException(f"HITL Stage 2 failed: {e}") from e
