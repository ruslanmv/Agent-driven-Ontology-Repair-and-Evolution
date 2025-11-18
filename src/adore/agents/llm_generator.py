"""LLM Generator Agent for proposing new axioms."""

from adore.agents.base import BaseAgent
from adore.core.constants import AgentType
from adore.core.exceptions import AgentException
from adore.core.models import Axiom, WorkflowState
from adore.services.llm_service import LLMService
from adore.services.ontology_service import OntologyService


class LLMGeneratorAgent(BaseAgent):
    """Agent that uses LLMs to propose new axioms for the ontology.

    This agent analyzes the current ontology state and generates a new
    candidate axiom that could expand the knowledge base.
    """

    def __init__(self, llm_service: LLMService, ontology_service: OntologyService) -> None:
        """Initialize the LLM Generator Agent.

        Args:
            llm_service: Service for LLM operations.
            ontology_service: Service for ontology operations.
        """
        super().__init__(AgentType.LLM_GENERATOR)
        self.llm_service = llm_service
        self.ontology_service = ontology_service

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Generate a new axiom candidate using the LLM.

        Args:
            state: Current workflow state.

        Returns:
            WorkflowState: Updated state with candidate_axiom.

        Raises:
            AgentException: If axiom generation fails.
        """
        try:
            self.logger.info("Starting axiom generation", cycle_id=state.cycle_id)

            # Load ontology if path provided
            if state.ontology_path:
                ontology = self.ontology_service.load_ontology(state.ontology_path)
                axioms = self.ontology_service.extract_axioms(ontology)
                ontology_context = "\n".join(f"{i+1}) {ax}" for i, ax in enumerate(axioms))
            else:
                ontology_context = "Empty ontology - please propose a foundational axiom."

            # Generate axiom using LLM
            task_description = (
                "Please propose a single new DL axiom that would expand this ontology. "
                "The axiom should be relevant, plausible, and in proper Description Logic syntax."
            )

            axiom_str = self.llm_service.generate_axiom(ontology_context, task_description)

            # Create Axiom model
            axiom = Axiom(content=axiom_str, source="llm_generator")
            state.candidate_axiom = axiom

            self.log_action(state, "proposed_axiom", {"axiom": axiom_str})
            self.logger.info("Axiom generated successfully", axiom=axiom_str)

            return state

        except Exception as e:
            self.logger.error("Axiom generation failed", error=str(e))
            self.log_action(state, "generation_failed", {"error": str(e)})
            raise AgentException(f"LLM Generator failed: {e}") from e
