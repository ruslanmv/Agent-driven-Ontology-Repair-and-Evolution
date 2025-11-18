"""Workflow orchestration service using LangGraph.

This service coordinates the ADORE multi-agent workflow.
"""

from typing import Any, Callable

from langgraph.graph import END, StateGraph

from adore.agents import (
    AxiomWeakeningAgent,
    ConsistencyGuardAgent,
    DomainExpertAgent,
    HITLStage1Agent,
    HITLStage2Agent,
    LinguisticInsightAgent,
    LLMGeneratorAgent,
    MetaKnowledgeAgent,
)
from adore.core.constants import WorkflowStrategy
from adore.core.exceptions import WorkflowException
from adore.core.models import WorkflowState
from adore.infrastructure.logging import get_logger
from adore.services.llm_service import LLMService
from adore.services.ontology_service import OntologyService

logger = get_logger(__name__)


class WorkflowOrchestrator:
    """Orchestrates the ADORE workflow using LangGraph.

    This class builds and executes the multi-agent workflow for
    ontology repair and evolution.
    """

    def __init__(
        self,
        llm_service: LLMService,
        ontology_service: OntologyService,
        auto_hitl: bool = True,
    ) -> None:
        """Initialize the workflow orchestrator.

        Args:
            llm_service: Service for LLM operations.
            ontology_service: Service for ontology operations.
            auto_hitl: Whether to run HITL stages in auto mode.
        """
        self.llm_service = llm_service
        self.ontology_service = ontology_service
        self.auto_hitl = auto_hitl

        # Initialize agents
        self.llm_gen = LLMGeneratorAgent(llm_service, ontology_service)
        self.dea = DomainExpertAgent(llm_service)
        self.lia = LinguisticInsightAgent()
        self.cga = ConsistencyGuardAgent(ontology_service)
        self.awea = AxiomWeakeningAgent(ontology_service)
        self.hitl1 = HITLStage1Agent(auto_mode=auto_hitl)
        self.hitl2 = HITLStage2Agent(auto_mode=auto_hitl)
        self.mka = MetaKnowledgeAgent(ontology_service)

        # Build workflow
        self.workflow = self._build_workflow()
        logger.info("Workflow orchestrator initialized")

    def _build_workflow(self) -> Any:
        """Build the LangGraph workflow.

        Returns:
            Compiled workflow graph.
        """
        # Create state graph
        builder = StateGraph(dict)

        # Add nodes (agents)
        builder.add_node("llm_gen", self._wrap_agent(self.llm_gen))
        builder.add_node("dea", self._wrap_agent(self.dea))
        builder.add_node("lia", self._wrap_agent(self.lia))
        builder.add_node("cga", self._wrap_agent(self.cga))
        builder.add_node("hitl1", self._wrap_agent(self.hitl1))
        builder.add_node("awea", self._wrap_agent(self.awea))
        builder.add_node("hitl2", self._wrap_agent(self.hitl2))
        builder.add_node("mka", self._wrap_agent(self.mka))

        # Set entry point
        builder.set_entry_point("llm_gen")

        # Add sequential edges
        builder.add_edge("llm_gen", "dea")
        builder.add_edge("dea", "lia")
        builder.add_edge("lia", "cga")
        builder.add_edge("cga", "hitl1")

        # Add conditional edges from HITL1
        builder.add_conditional_edges(
            "hitl1",
            self._route_after_hitl1,
            {
                "awea": "awea",
                "mka": "mka",
            },
        )

        # Add edges for repair path
        builder.add_edge("awea", "hitl2")
        builder.add_edge("hitl2", "mka")

        # Set end
        builder.add_edge("mka", END)

        # Compile
        workflow = builder.compile()
        logger.debug("Workflow graph compiled successfully")
        return workflow

    def _wrap_agent(self, agent: Any) -> Callable[[dict[str, Any]], dict[str, Any]]:
        """Wrap agent to work with LangGraph's dict-based state.

        Args:
            agent: The agent to wrap.

        Returns:
            Wrapped agent function.
        """

        def wrapped(state_dict: dict[str, Any]) -> dict[str, Any]:
            # Convert dict to WorkflowState
            state = WorkflowState(**state_dict)

            # Execute agent
            updated_state = agent.execute(state)

            # Convert back to dict
            return updated_state.model_dump()

        return wrapped

    def _route_after_hitl1(self, state: dict[str, Any]) -> str:
        """Determine routing after HITL Stage 1.

        Args:
            state: Current state dict.

        Returns:
            str: Next node name.
        """
        strategy = state.get("chosen_strategy")

        if strategy == WorkflowStrategy.ONTOLOGY_EVOLUTION.value:
            return "awea"
        else:
            return "mka"

    def run_cycle(self, initial_state: WorkflowState) -> WorkflowState:
        """Run a single ADORE cycle.

        Args:
            initial_state: Initial workflow state.

        Returns:
            WorkflowState: Final state after cycle completion.

        Raises:
            WorkflowException: If workflow execution fails.
        """
        try:
            logger.info("Starting ADORE cycle", cycle_id=initial_state.cycle_id)

            # Convert to dict for LangGraph
            state_dict = initial_state.model_dump()

            # Execute workflow
            result_dict = self.workflow.invoke(state_dict)

            # Convert back to WorkflowState
            final_state = WorkflowState(**result_dict)

            logger.info("ADORE cycle completed successfully", cycle_id=final_state.cycle_id)
            return final_state

        except Exception as e:
            logger.error("Workflow execution failed", error=str(e), cycle_id=initial_state.cycle_id)
            raise WorkflowException(f"Workflow execution failed: {e}") from e
