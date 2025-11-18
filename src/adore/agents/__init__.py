"""Agent implementations for the ADORE framework."""

from adore.agents.axiom_weakening import AxiomWeakeningAgent
from adore.agents.base import BaseAgent
from adore.agents.consistency_guard import ConsistencyGuardAgent
from adore.agents.domain_expert import DomainExpertAgent
from adore.agents.hitl import HITLStage1Agent, HITLStage2Agent
from adore.agents.linguistic_insight import LinguisticInsightAgent
from adore.agents.llm_generator import LLMGeneratorAgent
from adore.agents.meta_knowledge import MetaKnowledgeAgent

__all__ = [
    "BaseAgent",
    "LLMGeneratorAgent",
    "DomainExpertAgent",
    "LinguisticInsightAgent",
    "ConsistencyGuardAgent",
    "AxiomWeakeningAgent",
    "HITLStage1Agent",
    "HITLStage2Agent",
    "MetaKnowledgeAgent",
]
