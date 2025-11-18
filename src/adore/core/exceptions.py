"""Custom exceptions for ADORE framework.

This module defines all custom exceptions used throughout the ADORE system,
providing granular error handling and meaningful error messages.
"""


class AdoreException(Exception):
    """Base exception for all ADORE-related errors."""

    pass


class OntologyException(AdoreException):
    """Raised when ontology operations fail."""

    pass


class OntologyLoadError(OntologyException):
    """Raised when an ontology cannot be loaded."""

    pass


class OntologyConsistencyError(OntologyException):
    """Raised when an ontology is inconsistent."""

    pass


class AxiomParsingError(OntologyException):
    """Raised when an axiom cannot be parsed."""

    pass


class AgentException(AdoreException):
    """Base exception for agent-related errors."""

    pass


class LLMException(AgentException):
    """Raised when LLM operations fail."""

    pass


class WorkflowException(AdoreException):
    """Raised when workflow execution fails."""

    pass


class ConfigurationError(AdoreException):
    """Raised when configuration is invalid."""

    pass


class ValidationError(AdoreException):
    """Raised when data validation fails."""

    pass
