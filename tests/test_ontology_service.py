"""Tests for OntologyService."""

import tempfile
from pathlib import Path

import pytest
from owlready2 import Thing, ObjectProperty, get_ontology

from adore.services.ontology_service import OntologyService


@pytest.fixture
def ontology_service() -> OntologyService:
    """Create an OntologyService instance."""
    return OntologyService()


@pytest.fixture
def sample_ontology_path() -> Path:
    """Create a sample ontology file for testing."""
    onto = get_ontology("http://test.org/sample.owl")

    with onto:
        class Person(Thing):
            pass

        class hasName(ObjectProperty):
            domain = [Person]

    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".owl")
    temp_path = Path(temp_file.name)
    temp_file.close()

    onto.save(file=str(temp_path), format="rdfxml")

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


def test_create_ontology(ontology_service: OntologyService) -> None:
    """Test creating a new ontology."""
    ontology = ontology_service.create_ontology()

    assert ontology is not None
    assert ontology.base_iri == "http://example.org/adore_ontology.owl"


def test_load_ontology(ontology_service: OntologyService, sample_ontology_path: Path) -> None:
    """Test loading an ontology from a file."""
    ontology = ontology_service.load_ontology(sample_ontology_path)

    assert ontology is not None
    classes = list(ontology.classes())
    assert len(classes) > 0


def test_check_consistency(ontology_service: OntologyService) -> None:
    """Test consistency checking."""
    # Create a consistent ontology
    onto = get_ontology("http://test.org/consistent.owl")

    with onto:
        class Animal(Thing):
            pass

    assert ontology_service.check_consistency(onto) is True


def test_extract_axioms(ontology_service: OntologyService, sample_ontology_path: Path) -> None:
    """Test extracting axioms from an ontology."""
    ontology = ontology_service.load_ontology(sample_ontology_path)
    axioms = ontology_service.extract_axioms(ontology)

    assert isinstance(axioms, list)
    # Should have at least the Person ⊑ Thing axiom
    assert len(axioms) >= 1
