"""Ontology management service using Owlready2.

This service provides high-level operations for ontology manipulation,
reasoning, and consistency checking.
"""

import tempfile
from pathlib import Path
from typing import Any, Optional

import owlready2
from owlready2 import (
    AllValuesFrom,
    ExactCardinality,
    MaxCardinality,
    MinCardinality,
    ObjectProperty,
    Restriction,
    SomeValuesFrom,
    Thing,
    World,
    get_ontology,
    sync_reasoner,
)

from adore.core.exceptions import (
    AxiomParsingError,
    OntologyConsistencyError,
    OntologyException,
    OntologyLoadError,
)
from adore.infrastructure.logging import get_logger

logger = get_logger(__name__)


class OntologyService:
    """Service for managing OWL ontologies with Owlready2.

    This service provides a clean interface for ontology operations including
    loading, saving, reasoning, and consistency checking.
    """

    def __init__(self, ontology_iri: str = "http://example.org/adore_ontology.owl") -> None:
        """Initialize the ontology service.

        Args:
            ontology_iri: IRI for the ontology.
        """
        self.ontology_iri = ontology_iri
        self.ontology: Optional[owlready2.Ontology] = None
        self.temp_file_path: Optional[Path] = None
        logger.info("Initialized OntologyService", ontology_iri=ontology_iri)

    def create_ontology(self) -> owlready2.Ontology:
        """Create a new empty ontology.

        Returns:
            owlready2.Ontology: The created ontology.
        """
        logger.info("Creating new ontology")
        self.ontology = get_ontology(self.ontology_iri)
        return self.ontology

    def load_ontology(self, file_path: Path) -> owlready2.Ontology:
        """Load an ontology from a file.

        Args:
            file_path: Path to the OWL file.

        Returns:
            owlready2.Ontology: The loaded ontology.

        Raises:
            OntologyLoadError: If the ontology cannot be loaded.
        """
        try:
            logger.info("Loading ontology from file", file_path=str(file_path))
            file_iri = f"file://{file_path.absolute()}"
            self.ontology = get_ontology(file_iri).load()
            logger.info("Ontology loaded successfully", classes=len(list(self.ontology.classes())))
            return self.ontology
        except Exception as e:
            logger.error("Failed to load ontology", error=str(e), file_path=str(file_path))
            raise OntologyLoadError(f"Failed to load ontology from {file_path}: {e}") from e

    def save_ontology(self, file_path: Path, ontology: Optional[owlready2.Ontology] = None) -> None:
        """Save an ontology to a file.

        Args:
            file_path: Path where to save the ontology.
            ontology: Ontology to save. If None, uses self.ontology.

        Raises:
            OntologyException: If saving fails.
        """
        onto = ontology or self.ontology
        if onto is None:
            raise OntologyException("No ontology to save")

        try:
            logger.info("Saving ontology", file_path=str(file_path))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            onto.save(file=str(file_path), format="rdfxml")
            logger.info("Ontology saved successfully")
        except Exception as e:
            logger.error("Failed to save ontology", error=str(e))
            raise OntologyException(f"Failed to save ontology: {e}") from e

    def duplicate_ontology(self, source_ontology: owlready2.Ontology) -> tuple[owlready2.Ontology, Path]:
        """Create an isolated copy of an ontology.

        Args:
            source_ontology: The ontology to duplicate.

        Returns:
            tuple: (duplicated ontology, temporary file path)

        Raises:
            OntologyException: If duplication fails.
        """
        try:
            logger.debug("Duplicating ontology", ontology_name=source_ontology.name)

            # Create isolated world
            isolated_world = World()

            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".owl")
            temp_path = Path(temp_file.name)
            temp_file.close()

            source_ontology.save(file=str(temp_path), format="rdfxml")

            # Load in isolated world
            file_iri = f"file://{temp_path.absolute()}"
            copied_onto = isolated_world.get_ontology(file_iri).load()

            logger.debug(
                "Ontology duplicated",
                original=source_ontology.name,
                duplicate=copied_onto.name,
                temp_file=str(temp_path),
            )
            return copied_onto, temp_path

        except Exception as e:
            logger.error("Failed to duplicate ontology", error=str(e))
            raise OntologyException(f"Failed to duplicate ontology: {e}") from e

    def check_consistency(self, ontology: Optional[owlready2.Ontology] = None) -> bool:
        """Check if an ontology is logically consistent.

        Args:
            ontology: Ontology to check. If None, uses self.ontology.

        Returns:
            bool: True if consistent, False otherwise.
        """
        onto = ontology or self.ontology
        if onto is None:
            logger.warning("No ontology to check")
            return False

        temp_onto: Optional[owlready2.Ontology] = None
        temp_path: Optional[Path] = None

        try:
            # Duplicate for isolated reasoning
            temp_onto, temp_path = self.duplicate_ontology(onto)

            with temp_onto:
                sync_reasoner(infer_property_values=False)

            # Check for inconsistent classes
            inconsistent = list(temp_onto.world.inconsistent_classes())
            is_consistent = len(inconsistent) == 0

            if is_consistent:
                logger.debug("Ontology is consistent")
            else:
                logger.warning("Ontology is inconsistent", inconsistent_classes=[c.name for c in inconsistent])

            return is_consistent

        except Exception as e:
            logger.error("Consistency check failed", error=str(e))
            return False

        finally:
            # Cleanup
            if temp_onto and hasattr(temp_onto, "_world"):
                if temp_onto._world is not owlready2.default_world:
                    if hasattr(temp_onto._world, "closed") and not temp_onto._world.closed:
                        temp_onto._world.close()
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def extract_axioms(self, ontology: Optional[owlready2.Ontology] = None) -> list[str]:
        """Extract all axioms from an ontology in readable format.

        Args:
            ontology: Ontology to extract from. If None, uses self.ontology.

        Returns:
            list[str]: List of axiom strings in DL notation.
        """
        onto = ontology or self.ontology
        if onto is None:
            return []

        axioms: list[str] = []

        try:
            # Class axioms
            for cls in onto.classes():
                for sup in cls.is_a:
                    if isinstance(sup, (SomeValuesFrom, AllValuesFrom)):
                        restriction_type = "some" if isinstance(sup, SomeValuesFrom) else "all"
                        prop_name = sup.property.name if hasattr(sup.property, "name") else str(sup.property)
                        filler_name = sup.filler.name if hasattr(sup.filler, "name") else str(sup.filler)
                        axioms.append(f"{cls.name} ⊑ {prop_name} {restriction_type} {filler_name}")
                    elif isinstance(sup, (MinCardinality, MaxCardinality, ExactCardinality)):
                        r_type = "min" if isinstance(sup, MinCardinality) else ("max" if isinstance(sup, MaxCardinality) else "exactly")
                        prop_name = sup.property.name if hasattr(sup.property, "name") else str(sup.property)
                        filler_name = "owl.Thing"
                        if hasattr(sup, "filler") and sup.filler is not None and sup.filler is not Thing:
                            filler_name = sup.filler.name if hasattr(sup.filler, "name") else str(sup.filler)
                        axioms.append(
                            f"{cls.name} ⊑ {prop_name} {r_type} {sup.cardinality} {filler_name}"
                        )
                    elif hasattr(sup, "name"):
                        axioms.append(f"{cls.name} ⊑ {sup.name}")

            # Disjointness axioms
            for dis_axiom in onto.disjoint_classes():
                if hasattr(dis_axiom, "entities"):
                    entity_names = [e.name for e in dis_axiom.entities if hasattr(e, "name")]
                    if entity_names:
                        axioms.append(f"DisjointClasses({', '.join(entity_names)})")

        except Exception as e:
            logger.error("Failed to extract axioms", error=str(e))

        return axioms

    def add_axiom_from_string(
        self, axiom_str: str, ontology: Optional[owlready2.Ontology] = None
    ) -> None:
        """Parse and add an axiom from DL string notation.

        Args:
            axiom_str: Axiom in Description Logic notation (e.g., "Pneumonia ⊑ ∃causedBy.Bacterium")
            ontology: Target ontology. If None, uses self.ontology.

        Raises:
            AxiomParsingError: If the axiom cannot be parsed.
        """
        onto = ontology or self.ontology
        if onto is None:
            raise AxiomParsingError("No ontology available")

        try:
            logger.debug("Parsing axiom", axiom=axiom_str)

            # Parse basic subsumption with existential restriction
            if "⊑ ∃" in axiom_str and "." in axiom_str:
                lhs_str, rhs_str = [s.strip() for s in axiom_str.split("⊑")]
                prop_filler = rhs_str[1:]  # Remove ∃
                prop_name, filler_name = prop_filler.split(".", 1)

                # Get entities from ontology
                lhs_class = getattr(onto, lhs_str, None)
                prop = getattr(onto, prop_name, None)
                filler_class = getattr(onto, filler_name, None)

                if not all([lhs_class, prop, filler_class]):
                    raise AxiomParsingError(f"Cannot find required entities in ontology: {axiom_str}")

                if not issubclass(prop, ObjectProperty):
                    raise AxiomParsingError(f"{prop_name} is not an ObjectProperty")

                # Add axiom
                restriction = prop.some(filler_class)
                lhs_class.is_a.append(restriction)
                logger.info("Axiom added", axiom=axiom_str)
            else:
                raise AxiomParsingError(f"Unsupported axiom format: {axiom_str}")

        except Exception as e:
            logger.error("Failed to add axiom", axiom=axiom_str, error=str(e))
            raise AxiomParsingError(f"Failed to parse axiom '{axiom_str}': {e}") from e

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_file_path and self.temp_file_path.exists():
            try:
                self.temp_file_path.unlink()
                logger.debug("Cleaned up temp file", path=str(self.temp_file_path))
            except Exception as e:
                logger.warning("Failed to clean up temp file", error=str(e))
