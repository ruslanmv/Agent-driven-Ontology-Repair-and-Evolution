"""Constants used throughout the ADORE framework."""

from enum import Enum


class AgentType(str, Enum):
    """Enumeration of agent types in the ADORE system."""

    LLM_GENERATOR = "llm_generator"
    DOMAIN_EXPERT = "domain_expert"
    LINGUISTIC_INSIGHT = "linguistic_insight"
    CONSISTENCY_GUARD = "consistency_guard"
    AXIOM_WEAKENING = "axiom_weakening"
    HITL_STAGE1 = "hitl_stage1"
    HITL_STAGE2 = "hitl_stage2"
    META_KNOWLEDGE = "meta_knowledge"


class WorkflowStrategy(str, Enum):
    """Strategies for handling ontology evolution."""

    ACCEPT_AXIOM = "accept_axiom"
    ONTOLOGY_EVOLUTION = "ontology_evolution"
    REJECT_AXIOM = "reject_axiom"


class LogLevel(str, Enum):
    """Logging levels for structured logging."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Default configuration values
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 200
DEFAULT_REASONING_TIMEOUT = 30  # seconds

# Display constants for Rich CLI
ADORE_BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     █████╗ ██████╗  ██████╗ ██████╗ ███████╗                ║
║    ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔════╝                ║
║    ███████║██║  ██║██║   ██║██████╔╝█████╗                  ║
║    ██╔══██║██║  ██║██║   ██║██╔══██╗██╔══╝                  ║
║    ██║  ██║██████╔╝╚██████╔╝██║  ██║███████╗                ║
║    ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝                ║
║                                                               ║
║    Agent-Driven Ontology Repair and Evolution                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
