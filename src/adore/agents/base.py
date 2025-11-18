"""Base agent class and interfaces for ADORE agents.

This module defines the abstract base class that all ADORE agents inherit from,
providing a consistent interface for the workflow orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Any

from adore.core.constants import AgentType
from adore.core.models import WorkflowState
from adore.infrastructure.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all ADORE agents.

    Each agent in the ADORE workflow must inherit from this class and implement
    the execute method. This ensures a consistent interface for workflow orchestration.
    """

    def __init__(self, agent_type: AgentType) -> None:
        """Initialize the base agent.

        Args:
            agent_type: The type of this agent.
        """
        self.agent_type = agent_type
        self.logger = get_logger(f"{__name__}.{agent_type.value}")

    @abstractmethod
    def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute the agent's logic and update the workflow state.

        Args:
            state: Current workflow state.

        Returns:
            WorkflowState: Updated workflow state.

        Raises:
            AgentException: If execution fails.
        """
        pass

    def log_action(self, state: WorkflowState, action: str, data: dict[str, Any] | None = None) -> None:
        """Log an agent action to the workflow state.

        Args:
            state: Current workflow state.
            action: Description of the action.
            data: Optional additional data.
        """
        state.add_log(self.agent_type, action, data or {})
        self.logger.info(
            f"Agent action: {action}",
            agent=self.agent_type.value,
            cycle_id=state.cycle_id,
            **data or {},
        )

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(type={self.agent_type.value})"
