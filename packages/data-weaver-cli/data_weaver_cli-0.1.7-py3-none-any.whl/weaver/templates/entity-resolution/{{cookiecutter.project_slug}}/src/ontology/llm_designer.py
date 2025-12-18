"""
LLM-Based Ontology Designer

This module uses LLMs to design knowledge graph ontologies based on database schemas.
Supports multiple LLM providers and iterative refinement.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass
class OntologyClass:
    """Represents an entity class in the ontology."""
    name: str
    description: str
    properties: List[str]
    parent_class: Optional[str] = None
    source_tables: List[str] = None

    def __post_init__(self):
        if self.source_tables is None:
            self.source_tables = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OntologyProperty:
    """Represents a property/attribute in the ontology."""
    name: str
    description: str
    data_type: str
    domain: List[str]  # Which classes can have this property
    range: Optional[str] = None  # The type/class of the value
    is_required: bool = False
    is_unique: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OntologyRelationship:
    """Represents a relationship between classes."""
    name: str
    description: str
    source_class: str
    target_class: str
    cardinality: str  # one-to-one, one-to-many, many-to-many
    inverse_name: Optional[str] = None
    source_foreign_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Ontology:
    """Complete ontology definition."""
    name: str
    description: str
    classes: List[OntologyClass]
    properties: List[OntologyProperty]
    relationships: List[OntologyRelationship]
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'metadata': self.metadata,
            'classes': [c.to_dict() for c in self.classes],
            'properties': [p.to_dict() for p in self.properties],
            'relationships': [r.to_dict() for r in self.relationships]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class OntologyDesigner:
    """Designs ontologies using LLMs based on database schemas."""

    def __init__(
            self,
            provider: LLMProvider = LLMProvider.ANTHROPIC,
            api_key: Optional[str] = None,
            model: Optional[str] = None
    ):
        """
        Initialize the ontology designer.

        Args:
            provider: LLM provider to use
            api_key: API key for the provider (if None, will use environment variables)
            model: Specific model to use (if None, will use provider defaults)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self._client = None

    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        if self.provider == LLMProvider.ANTHROPIC:
            key = os.getenv('ANTHROPIC_API_KEY')
            if not key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            return key
        elif self.provider == LLMProvider.OPENAI:
            key = os.getenv('OPENAI_API_KEY')
            if not key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            return key
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _get_default_model(self) -> str:
        """Get default model for the provider."""
        if self.provider == LLMProvider.ANTHROPIC:
            return "claude-sonnet-4-20250514"
        elif self.provider == LLMProvider.OPENAI:
            return "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _get_client(self):
        """Get or create LLM client."""
        if self._client is None:
            if self.provider == LLMProvider.ANTHROPIC:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            elif self.provider == LLMProvider.OPENAI:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
        return self._client

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call the LLM with the given prompt."""
        client = self._get_client()

        if self.provider == LLMProvider.ANTHROPIC:
            message = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt if system_prompt else "You are an expert ontology designer.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text

        elif self.provider == LLMProvider.OPENAI:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def design_ontology(
            self,
            schema_dict: Dict[str, Any],
            ontology_name: str,
            domain_context: Optional[str] = None,
            design_goals: Optional[List[str]] = None,
            entity_resolution_focus: bool = True
    ) -> Ontology:
        """
        Design an ontology based on a database schema.

        Args:
            schema_dict: Database schema as dictionary (from SchemaInspector)
            ontology_name: Name for the ontology
            domain_context: Additional context about the domain
            design_goals: Specific goals for the ontology design
            entity_resolution_focus: Whether to optimize for entity resolution

        Returns:
            Ontology object
        """
        # Build the prompt
        prompt = self._build_design_prompt(
            schema_dict,
            ontology_name,
            domain_context,
            design_goals,
            entity_resolution_focus
        )

        system_prompt = self._build_system_prompt()

        # Call LLM
        response = self._call_llm(prompt, system_prompt)

        # Parse response into Ontology object
        ontology = self._parse_ontology_response(response, ontology_name, schema_dict)

        return ontology

    def _build_system_prompt(self) -> str:
        """Build the system prompt for ontology design."""
        return """You are an expert ontology designer specializing in knowledge graphs and entity resolution.

Your task is to analyze database schemas and design high-quality ontologies that:
1. Capture the essential entities, attributes, and relationships in the domain
2. Follow ontology design best practices
3. Support entity resolution and data integration use cases
4. Are practical and implementable

You will respond with valid JSON that follows the specified schema structure.
Be thorough but pragmatic - focus on the most important entities and relationships."""

    def _build_design_prompt(
            self,
            schema_dict: Dict[str, Any],
            ontology_name: str,
            domain_context: Optional[str],
            design_goals: Optional[List[str]],
            entity_resolution_focus: bool
    ) -> str:
        """Build the main design prompt."""

        # Format schema information
        schema_json = json.dumps(schema_dict, indent=2)

        # Extract key information for easier processing
        tables_summary = []
        for table in schema_dict.get('tables', []):
            tables_summary.append({
                'name': table['name'],
                'columns': [c['name'] for c in table['columns']],
                'primary_keys': table['primary_keys'],
                'foreign_keys': len(table['foreign_keys']),
                'row_count': table.get('row_count', 'unknown')
            })

        prompt = f"""# Ontology Design Task

Design a knowledge graph ontology for the following database schema.

## Ontology Name
{ontology_name}

## Domain Context
{domain_context if domain_context else "No additional context provided"}

## Design Goals
{chr(10).join(f"- {goal}" for goal in design_goals) if design_goals else "- Create a comprehensive and practical ontology"}

{"## Entity Resolution Focus" if entity_resolution_focus else ""}
{'''This ontology will be used for entity resolution, so please:
- Identify natural key attributes that can be used for matching
- Consider canonical entity patterns
- Include properties useful for deduplication
- Design relationships that support entity linking''' if entity_resolution_focus else ""}

## Database Schema Summary

**Database:** {schema_dict.get('database_name', 'Unknown')}
**Schemas:** {', '.join(schema_dict.get('schemas', []))}
**Total Tables:** {len(schema_dict.get('tables', []))}

### Tables Overview
{json.dumps(tables_summary, indent=2)}

## Complete Schema Details
{schema_json}

## Your Task

Analyze this schema and design an ontology by identifying:

1. **Entity Classes** - The main entity types in the domain
   - Name each class clearly
   - Provide a description
   - List the key properties for each class
   - Identify any parent-child (is-a) relationships
   - Map which database table(s) correspond to each class

2. **Properties** - The attributes that describe entities
   - Name each property
   - Describe what it represents
   - Specify the data type
   - List which classes (domain) can have this property
   - Indicate if it's required or unique
   - For object properties, specify the range (target class)

3. **Relationships** - How entities relate to each other
   - Name each relationship (and its inverse if applicable)
   - Describe the relationship
   - Specify source and target classes
   - Indicate cardinality (one-to-one, one-to-many, many-to-many)
   - Map to the database foreign key if applicable

## Response Format

Respond with a valid JSON object following this exact structure:

```json
{
  "description": "Brief description of what this ontology models",
  "classes": [
    {
      "name": "EntityClassName",
      "description": "What this entity represents",
      "properties": ["property1", "property2"],
      "parent_class": "ParentClassName or null",
      "source_tables": ["table_name1", "table_name2"]
    }
  ],
  "properties": [
    {
      "name": "propertyName",
      "description": "What this property represents",
      "data_type": "string|integer|float|boolean|date|datetime",
      "domain": ["ClassName1", "ClassName2"],
      "range": "TargetClassName or null for literal values",
      "is_required": false,
      "is_unique": false
    }
  ],
  "relationships": [
    {
      "name": "relationshipName",
      "description": "What this relationship represents",
      "source_class": "SourceClassName",
      "target_class": "TargetClassName",
      "cardinality": "one-to-one|one-to-many|many-to-many",
      "inverse_name": "inverseRelationshipName or null",
      "source_foreign_key": "foreign_key_name or null"
    }
  ]
}
```

## Important Guidelines

1. **Entity vs Junction Tables**: Distinguish between entities (things in the domain) and junction tables (just connecting other entities)
2. **Naming**: Use clear, domain-appropriate names (PascalCase for classes, camelCase for properties)
3. **Granularity**: Find the right level - not too abstract, not too specific
4. **Relationships**: Model direct relationships, avoid creating relationships that are just attribute-based joins
5. **Properties**: Include the most important properties, but don't overwhelm with every column
6. **Hierarchy**: Only use parent_class when there's a true is-a relationship

Return ONLY the JSON object, no additional text or markdown formatting."""

        return prompt

    def _parse_ontology_response(
            self,
            response: str,
            ontology_name: str,
            schema_dict: Dict[str, Any]
    ) -> Ontology:
        """Parse LLM response into Ontology object."""
        # Clean response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```'):
            # Remove opening ```json or ```
            lines = response.split('\n')
            lines = lines[1:]  # Remove first line
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove last line
            response = '\n'.join(lines)

        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {response}")

        # Create Ontology object
        ontology = Ontology(
            name=ontology_name,
            description=data.get('description', ''),
            classes=[
                OntologyClass(**cls) for cls in data.get('classes', [])
            ],
            properties=[
                OntologyProperty(**prop) for prop in data.get('properties', [])
            ],
            relationships=[
                OntologyRelationship(**rel) for rel in data.get('relationships', [])
            ],
            metadata={
                'source_database': schema_dict.get('database_name'),
                'source_schemas': schema_dict.get('schemas', []),
                'total_source_tables': len(schema_dict.get('tables', []))
            }
        )

        return ontology

    def refine_ontology(
            self,
            ontology: Ontology,
            schema_dict: Dict[str, Any],
            feedback: str
    ) -> Ontology:
        """
        Refine an existing ontology based on user feedback.

        Args:
            ontology: The current ontology
            schema_dict: Original database schema
            feedback: User feedback on what to change

        Returns:
            Refined Ontology object
        """
        prompt = f"""# Ontology Refinement Task

You previously designed the following ontology:

## Current Ontology
{ontology.to_json()}

## User Feedback
{feedback}

## Original Database Schema
{json.dumps(schema_dict, indent=2)}

## Your Task

Refine the ontology based on the user's feedback while maintaining consistency with the database schema.

Return the complete refined ontology in the same JSON format as before.

Return ONLY the JSON object, no additional text or markdown formatting."""

        system_prompt = "You are an expert ontology designer. Refine the given ontology based on user feedback."

        response = self._call_llm(prompt, system_prompt)

        return self._parse_ontology_response(response, ontology.name, schema_dict)

    def explain_design_decisions(
            self,
            ontology: Ontology,
            schema_dict: Dict[str, Any]
    ) -> str:
        """
        Get an explanation of the design decisions made.

        Args:
            ontology: The designed ontology
            schema_dict: Original database schema

        Returns:
            Explanation text
        """
        prompt = f"""# Explain Ontology Design

You designed the following ontology based on a database schema:

## Ontology
{ontology.to_json()}

## Database Schema
{json.dumps(schema_dict, indent=2)}

## Your Task

Provide a clear explanation of the key design decisions you made:

1. **Entity Class Choices**: Why did you choose these entity classes? Which tables did you exclude and why?
2. **Property Selection**: How did you decide which properties to include?
3. **Relationship Modeling**: Explain the key relationships and why you modeled them this way
4. **Design Trade-offs**: What trade-offs did you make?
5. **Entity Resolution Considerations**: How does this ontology support entity resolution?

Be concise but thorough."""

        system_prompt = "You are an expert ontology designer explaining your design decisions."

        return self._call_llm(prompt, system_prompt)

    def suggest_improvements(
            self,
            ontology: Ontology,
            schema_dict: Dict[str, Any]
    ) -> List[str]:
        """
        Get suggestions for improving the ontology.

        Args:
            ontology: The current ontology
            schema_dict: Original database schema

        Returns:
            List of improvement suggestions
        """
        prompt = f"""# Ontology Improvement Suggestions

Review the following ontology and suggest improvements:

## Ontology
{ontology.to_json()}

## Database Schema
{json.dumps(schema_dict, indent=2)}

## Your Task

Analyze this ontology and suggest 3-5 concrete improvements. Consider:
- Missing important entities or relationships
- Overly complex or simplified areas
- Better naming or organization
- Additional properties that would be valuable
- Entity resolution capabilities

Format your response as a JSON array of strings:
["suggestion 1", "suggestion 2", "suggestion 3"]

Return ONLY the JSON array."""

        system_prompt = "You are an expert ontology designer providing constructive feedback."

        response = self._call_llm(prompt, system_prompt)

        # Parse response
        response = response.strip()
        if response.startswith('```'):
            lines = response.split('\n')
            lines = lines[1:-1]
            response = '\n'.join(lines)

        return json.loads(response)


def main():
    """Example usage of the OntologyDesigner."""
    import sys
    from schema_inspector import SchemaInspector

    if len(sys.argv) < 2:
        print("Usage: python llm_designer.py <connection_string> [ontology_name]")
        print("Example: python llm_designer.py 'postgresql://user:pass@localhost/dbname' MyOntology")
        sys.exit(1)

    connection_string = sys.argv[1]
    ontology_name = sys.argv[2] if len(sys.argv) > 2 else "GeneratedOntology"

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)

    print("Step 1: Inspecting database schema...")
    with SchemaInspector(connection_string) as inspector:
        schema = inspector.inspect(include_row_counts=True)
        schema_dict = schema.to_dict()

    print(f"Found {len(schema.tables)} tables in database '{schema.database_name}'")

    print("\nStep 2: Designing ontology with LLM...")
    designer = OntologyDesigner(provider=LLMProvider.ANTHROPIC)

    ontology = designer.design_ontology(
        schema_dict=schema_dict,
        ontology_name=ontology_name,
        domain_context="This is an entity resolution system",
        entity_resolution_focus=True
    )

    print(f"\nOntology designed: {ontology.name}")
    print(f"  Classes: {len(ontology.classes)}")
    print(f"  Properties: {len(ontology.properties)}")
    print(f"  Relationships: {len(ontology.relationships)}")

    # Save ontology
    output_file = f"{ontology_name.lower()}_ontology.json"
    with open(output_file, 'w') as f:
        f.write(ontology.to_json())
    print(f"\nOntology saved to: {output_file}")

    # Get explanation
    print("\nStep 3: Getting design explanation...")
    explanation = designer.explain_design_decisions(ontology, schema_dict)
    print("\n" + "=" * 80)
    print("DESIGN EXPLANATION")
    print("=" * 80)
    print(explanation)

    # Get suggestions
    print("\nStep 4: Getting improvement suggestions...")
    suggestions = designer.suggest_improvements(ontology, schema_dict)
    print("\n" + "=" * 80)
    print("IMPROVEMENT SUGGESTIONS")
    print("=" * 80)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")


if __name__ == "__main__":
    main()