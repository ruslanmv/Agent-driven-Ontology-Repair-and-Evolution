"""Core domain models for ADORE framework using Pydantic V2.

This module defines all data models used throughout the ADORE system,
ensuring type safety and data validation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from adore.core.constants import AgentType, WorkflowStrategy


class Assessment(BaseModel):
    """Model for agent assessment results.

    Attributes:
        score: Confidence score between 0.0 and 1.0.
        justification: Textual explanation of the assessment.
        metadata: Additional metadata about the assessment.
    """

    score: float = Field(ge=0.0, le=1.0, description="Assessment confidence score")
    justification: str = Field(min_length=1, description="Assessment rationale")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Validate that score is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class Axiom(BaseModel):
    """Model representing a Description Logic axiom.

    Attributes:
        content: The axiom in Description Logic notation.
        source: Source of the axiom (e.g., 'llm', 'manual', 'repair').
        timestamp: When the axiom was created.
        metadata: Additional axiom metadata.
    """

    content: str = Field(min_length=1, description="Axiom in DL notation")
    source: str = Field(default="unknown", description="Origin of the axiom")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": False}


class RepairProposal(BaseModel):
    """Model for ontology repair proposals.

    Attributes:
        justification: Explanation of the repair strategy.
        modified_axioms: List of axioms that were modified.
        added_axioms: List of newly added axioms.
        removed_axioms: List of removed axioms.
        is_consistent: Whether the repaired ontology is consistent.
        metadata: Additional repair metadata.
    """

    justification: str = Field(min_length=1)
    modified_axioms: list[str] = Field(default_factory=list)
    added_axioms: list[str] = Field(default_factory=list)
    removed_axioms: list[str] = Field(default_factory=list)
    is_consistent: bool = Field(default=False)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentLog(BaseModel):
    """Model for agent action logging.

    Attributes:
        agent_type: Type of agent that performed the action.
        action: Description of the action performed.
        timestamp: When the action occurred.
        data: Additional data associated with the action.
    """

    agent_type: AgentType
    action: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.now)
    data: dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True}


class WorkflowState(BaseModel):
    """Model representing the complete state of an ADORE workflow.

    This model captures all information needed to execute and track
    an ontology evolution cycle.

    Attributes:
        cycle_id: Unique identifier for this workflow cycle.
        ontology_path: Path to the current ontology file.
        candidate_axiom: The axiom being evaluated.
        dea_assessment: Domain Expert Agent assessment.
        lia_assessment: Linguistic Insight Agent assessment.
        is_consistent: Whether candidate axiom is consistent.
        inconsistent_axioms: List of conflicting axioms if inconsistent.
        chosen_strategy: Strategy chosen by HITL.
        repair_proposals: List of repair proposals.
        final_ontology_path: Path to final ontology after cycle.
        logs: Complete log of all agent actions.
        metadata: Additional workflow metadata.
    """

    cycle_id: int = Field(ge=1, description="Workflow cycle identifier")
    ontology_path: Optional[Path] = None
    candidate_axiom: Optional[Axiom] = None
    dea_assessment: Optional[Assessment] = None
    lia_assessment: Optional[Assessment] = None
    is_consistent: bool = True
    inconsistent_axioms: list[str] = Field(default_factory=list)
    chosen_strategy: Optional[WorkflowStrategy] = None
    repair_proposals: list[RepairProposal] = Field(default_factory=list)
    final_ontology_path: Optional[Path] = None
    logs: list[AgentLog] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True, "use_enum_values": True}

    def add_log(self, agent_type: AgentType, action: str, data: dict[str, Any] | None = None) -> None:
        """Add a log entry for an agent action.

        Args:
            agent_type: The type of agent performing the action.
            action: Description of the action.
            data: Optional additional data.
        """
        log = AgentLog(agent_type=agent_type, action=action, data=data or {})
        self.logs.append(log)


class CycleReport(BaseModel):
    """Model for the final cycle report generated by Meta-Knowledge Agent.

    Attributes:
        cycle_id: The workflow cycle identifier.
        candidate_axiom: The evaluated axiom.
        assessments: All agent assessments.
        consistency_result: Final consistency check result.
        strategy: Chosen evolution strategy.
        repair_applied: Whether a repair was applied.
        final_axioms: List of axioms in final ontology.
        execution_time_seconds: Total execution time.
        timestamp: When the report was generated.
    """

    cycle_id: int
    candidate_axiom: Optional[str] = None
    assessments: dict[str, Assessment] = Field(default_factory=dict)
    consistency_result: bool = True
    strategy: Optional[WorkflowStrategy] = None
    repair_applied: bool = False
    final_axioms: list[str] = Field(default_factory=list)
    execution_time_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {"use_enum_values": True}
