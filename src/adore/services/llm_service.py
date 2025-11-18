"""LLM service for interacting with language models.

This service provides a unified interface for LLM operations,
supporting both OpenAI and IBM Watsonx.
"""

from typing import Any, Optional

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from adore.core.exceptions import LLMException
from adore.infrastructure.config import get_settings
from adore.infrastructure.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for LLM operations with multiple backend support.

    Supports OpenAI GPT models and can be extended for IBM Watsonx.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """Initialize the LLM service.

        Args:
            model_name: Name of the LLM model to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
        """
        settings = get_settings()

        self.model_name = model_name or settings.llm_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens

        logger.info(
            "Initializing LLM service",
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                openai_api_key=settings.openai_api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            logger.info("LLM service initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize LLM", error=str(e))
            raise LLMException(f"Failed to initialize LLM: {e}") from e

    def invoke(self, messages: list[BaseMessage]) -> AIMessage:
        """Invoke the LLM with a list of messages.

        Args:
            messages: List of messages to send to the LLM.

        Returns:
            AIMessage: The LLM's response.

        Raises:
            LLMException: If the LLM invocation fails.
        """
        try:
            logger.debug("Invoking LLM", num_messages=len(messages))
            response = self.llm.invoke(messages)

            if not isinstance(response, AIMessage):
                response = AIMessage(content=str(response))

            logger.debug("LLM response received", response_length=len(response.content))
            return response

        except Exception as e:
            logger.error("LLM invocation failed", error=str(e))
            raise LLMException(f"LLM invocation failed: {e}") from e

    def generate_text(self, prompt: str) -> str:
        """Generate text from a simple prompt.

        Args:
            prompt: The prompt text.

        Returns:
            str: Generated text.

        Raises:
            LLMException: If generation fails.
        """
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.invoke(messages)
            return response.content.strip()
        except Exception as e:
            logger.error("Text generation failed", error=str(e))
            raise LLMException(f"Text generation failed: {e}") from e

    def generate_axiom(self, ontology_context: str, task_description: str) -> str:
        """Generate a Description Logic axiom based on context.

        Args:
            ontology_context: Current ontology axioms as context.
            task_description: What kind of axiom to generate.

        Returns:
            str: Generated axiom in DL notation.

        Raises:
            LLMException: If axiom generation fails.
        """
        prompt = f"""Given the ontology axioms:
{ontology_context}

{task_description}

Output exactly one line with the axiom in Description Logic syntax.
Use the format: Class ⊑ ∃property.Filler
"""

        try:
            axiom = self.generate_text(prompt)
            # Extract first line if multiple lines returned
            axiom = axiom.strip().splitlines()[0]
            logger.info("Generated axiom", axiom=axiom)
            return axiom
        except Exception as e:
            logger.error("Axiom generation failed", error=str(e))
            raise LLMException(f"Axiom generation failed: {e}") from e

    def assess_axiom(self, axiom: str, assessment_type: str, criteria: str) -> dict[str, Any]:
        """Assess an axiom based on specific criteria.

        Args:
            axiom: The axiom to assess.
            assessment_type: Type of assessment (e.g., "domain_expert", "linguistic").
            criteria: Assessment criteria.

        Returns:
            dict: Assessment result with score and justification.

        Raises:
            LLMException: If assessment fails.
        """
        prompt = f"""As a {assessment_type}, assess the following axiom:

Axiom: {axiom}

Criteria: {criteria}

Provide your assessment as a JSON object with:
- "score": a number between 0.0 and 1.0
- "justification": a brief explanation

Example: {{"score": 0.8, "justification": "The axiom is well-formed and plausible."}}
"""

        try:
            response = self.generate_text(prompt)

            # Try to extract JSON from response
            import json
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback: create a simple assessment
                logger.warning("Could not parse JSON from LLM response, using fallback")
                return {"score": 0.5, "justification": response[:200]}

        except Exception as e:
            logger.error("Axiom assessment failed", error=str(e))
            raise LLMException(f"Axiom assessment failed: {e}") from e
