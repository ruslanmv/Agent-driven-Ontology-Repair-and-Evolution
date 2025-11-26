# ADORE Project Summary

ADORE, short for **Agent-Driven Ontology Repair and Evolution**, is an innovative framework designed to tackle the challenges introduced by integrating Large Language Models (LLMs) with formal ontologies. The project is aimed at enhancing knowledge base enrichment while maintaining logical consistency and trustworthiness.

## Overview

In the advent of utilizing LLMs, the fusion of rich semantic capabilities with rigorous logical structure presents both opportunities and significant hurdles. ADORE addresses these challenges through a multi-agent system (MAS) that plays a crucial role in the ontology evolution process. Instead of viewing inconsistencies merely as errors, ADORE treats them as catalysts for principled ontology evolution. 

Key components of ADORE include:
- **Axiom Weakening**: This is employed as a primary repair mechanism to handle logical inconsistencies without losing vital information.
- **Multi-Agent System (MAS)**: This system comprises specialized agents that each contribute distinct expertise to assess and repair ontological knowledge.
- **Human-in-the-Loop (HITL)**: ADORE integrates human oversight to ensure that the evolution process is transparent and explainable.

## Workflow

The ADORE system operates through a systematic process where proposals for new knowledge (axioms) are generated, assessed, and integrated into existing ontologies. The workflow consists of multiple stages:
1. **Environment Setup**: Loading and preparing the ontology.
2. **Axiom Generation**: LLM proposes new axioms based on current knowledge.
3. **Assessment**: Specialized agents evaluate the plausibility and correctness of proposed axioms.
4. **Consistency Checking**: New axioms are tested for logical consistency against existing knowledge.
5. **Human Decisions**: At crucial checkpoints, human input is sought to guide the ontology evolution based on expert judgment.
6. **Repair Mechanisms**: Identified inconsistencies are addressed through formal axioms weakening.
7. **Knowledge Consolidation**: The finalized ontology is updated based on accepted changes, and the entire evolution process is logged for future reference.

## Demonstration

The practical aspects of the ADORE framework are encapsulated in the Jupyter Notebook `ADORE_Demo.ipynb`, which provides a detailed and interactive demonstration of the entire workflow. Users are guided through a typical cycle of ontology evolution, observing how new knowledge is proposed, evaluated, and integrated.

## Research Implementation

ADORE is not only a conceptual framework but a working implementation that showcases the potential for advanced ontology management in collaboration with LLMs. The framework helps foster more trustworthy AI systems capable of dynamic and coherent knowledge evolution, paving the way for enhanced knowledge co-evolution systems.

## Contribution and Licensing

Developers and researchers are encouraged to contribute to the ADORE project by providing feedback, reporting issues, or submitting improvements. The code is released under the MIT License, promoting open collaboration while ensuring rights for the original authors.

By establishing a robust methodology for ontology repair and evolution, ADORE stands as a significant advancement in the realm of explainable AI and knowledge base management.