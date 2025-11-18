"""Tests for ADORE agents."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from adore.agents.domain_expert import DomainExpertAgent
from adore.agents.linguistic_insight import LinguisticInsightAgent
from adore.core.models import Axiom, WorkflowState


@pytest.fixture
def sample_state() -> WorkflowState:
    """Create a sample workflow state."""
    state = WorkflowState(cycle_id=1)
    state.candidate_axiom = Axiom(content="Pneumonia ⊑ ∃causedBy.Bacterium")
    return state


def test_linguistic_insight_agent(sample_state: WorkflowState) -> None:
    """Test LinguisticInsightAgent assessment."""
    agent = LinguisticInsightAgent()

    result_state = agent.execute(sample_state)

    assert result_state.lia_assessment is not None
    assert 0.0 <= result_state.lia_assessment.score <= 1.0
    assert len(result_state.lia_assessment.justification) > 0


def test_domain_expert_agent_with_mock_llm(sample_state: WorkflowState) -> None:
    """Test DomainExpertAgent with mocked LLM."""
    # Create mock LLM service
    mock_llm = MagicMock()
    mock_llm.assess_axiom.return_value = {
        "score": 0.85,
        "justification": "Medically plausible axiom"
    }

    agent = DomainExpertAgent(mock_llm)
    result_state = agent.execute(sample_state)

    assert result_state.dea_assessment is not None
    assert result_state.dea_assessment.score == 0.85
    assert "plausible" in result_state.dea_assessment.justification.lower()


def test_linguistic_insight_invalid_axiom() -> None:
    """Test LinguisticInsightAgent with invalid axiom."""
    state = WorkflowState(cycle_id=1)
    state.candidate_axiom = Axiom(content="invalid")

    agent = LinguisticInsightAgent()
    result_state = agent.execute(state)

    # Should still complete but with lower score
    assert result_state.lia_assessment is not None
    assert result_state.lia_assessment.score < 0.5
