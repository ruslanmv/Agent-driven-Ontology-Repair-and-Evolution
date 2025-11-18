"""Tests for workflow orchestration."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from owlready2 import Thing, get_ontology

from adore.core.models import WorkflowState
from adore.services.llm_service import LLMService
from adore.services.ontology_service import OntologyService
from adore.services.workflow_service import WorkflowOrchestrator


@pytest.fixture
def test_ontology_path() -> Path:
    """Create a test ontology."""
    onto = get_ontology("http://test.org/workflow_test.owl")

    with onto:
        class TestClass(Thing):
            pass

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".owl")
    temp_path = Path(temp_file.name)
    temp_file.close()

    onto.save(file=str(temp_path), format="rdfxml")

    yield temp_path

    if temp_path.exists():
        temp_path.unlink()


def test_workflow_state_creation() -> None:
    """Test creating a WorkflowState."""
    state = WorkflowState(cycle_id=1)

    assert state.cycle_id == 1
    assert state.is_consistent is True
    assert len(state.logs) == 0


def test_workflow_state_add_log() -> None:
    """Test adding logs to WorkflowState."""
    from adore.core.constants import AgentType

    state = WorkflowState(cycle_id=1)
    state.add_log(AgentType.LLM_GENERATOR, "test_action", {"key": "value"})

    assert len(state.logs) == 1
    assert state.logs[0].agent_type == AgentType.LLM_GENERATOR
    assert state.logs[0].action == "test_action"
