"""ADORE: Agent-Driven Ontology Repair and Evolution.

A revolutionary framework for intelligent knowledge base evolution using
multi-agent systems and large language models.
"""

__version__ = "1.0.0"
__authors__ = ["Ruslan Magana", "Marco Monti"]
__license__ = "Apache-2.0"

from adore.core.models import WorkflowState
from adore.services.llm_service import LLMService
from adore.services.ontology_service import OntologyService
from adore.services.workflow_service import WorkflowOrchestrator

__all__ = [
    "__version__",
    "WorkflowState",
    "LLMService",
    "OntologyService",
    "WorkflowOrchestrator",
]
