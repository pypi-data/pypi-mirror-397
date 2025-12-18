"""
PostgreSQL Schema Inspector for Ontology Generation

This module introspects PostgreSQL databases to extract schema information
that can be used by LLMs to design knowledge graph ontologies.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import json


@dataclass
class Column:
    """Represents a database column with its metadata."""
    name: str
    data_type: str
    is_nullable: bool
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    column_default: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_unique: bool = False
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ForeignKey:
    """Represents a foreign key relationship."""
    constraint_name: str
    source_table: str
    source_columns: List[str]
    target_table: str
    target_columns: List[str]
    on_delete: Optional[str] = None
    on_update: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Index:
    """Represents a database index."""
    name: str
    table_name: str
    columns: List[str]
    is_unique: bool
    is_primary: bool
    index_type: str  # btree, hash, gist, etc.

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Table:
    """Represents a database table with its complete metadata."""
    name: str
    schema: str
    columns: List[Column]
    primary_keys: List[str]
    foreign_keys: List[ForeignKey]
    indexes: List[Index]
    row_count: Optional[int] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with nested structures."""
        return {
            'name': self.name,
            'schema': self.schema,
            'description': self.description,
            'row_count': self.row_count,
            'columns': [col.to_dict() for col in self.columns],
            'primary_keys': self.primary_keys,
            'foreign_keys': [fk.to_dict() for fk in self.foreign_keys],
            'indexes': [idx.to_dict() for idx in self.indexes]
        }


@dataclass
class DatabaseSchema:
    """Complete database schema information."""
    database_name: str
    tables: List[Table]
    schemas: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'database_name': self.database_name,
            'schemas': self.schemas,
            'tables': [table.to_dict() for table in self.tables]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def get_relationships(self) -> List[Dict[str, Any]]:
        """Extract all relationships for easier LLM processing."""
        relationships = []
        for table in self.tables:
            for fk in table.foreign_keys:
                relationships.append({
                    'type': 'foreign_key',
                    'from_table': fk.source_table,
                    'from_columns': fk.source_columns,
                    'to_table': fk.target_table,
                    'to_columns': fk.target_columns,
                    'cardinality': self._infer_cardinality(fk)
                })
        return relationships

    def _infer_cardinality(self, fk: ForeignKey) -> str:
        """Infer relationship cardinality based on uniqueness constraints."""
        # Find source table
        source_table = next((t for t in self.tables if t.name == fk.source_table), None)
        if not source_table:
            return "many-to-one"

        # Check if foreign key columns are unique
        for idx in source_table.indexes:
            if idx.is_unique and set(fk.source_columns).issubset(set(idx.columns)):
                return "one-to-one"

        return "many-to-one"

    def get_entity_candidates(self) -> List[Dict[str, Any]]:
        """Identify tables that are likely entity types (vs. junction/lookup tables)."""
        candidates = []

        for table in self.tables:
            # Heuristics for entity identification
            score = 0
            reasons = []

            # Has multiple non-foreign-key columns
            non_fk_columns = [c for c in table.columns if not c.is_foreign_key]
            if len(non_fk_columns) >= 3:
                score += 2
                reasons.append("Has multiple attributes")

            # Has significant data
            if table.row_count and table.row_count > 10:
                score += 1
                reasons.append("Contains significant data")

            # Not a many-to-many junction table
            if not self._is_junction_table(table):
                score += 2
                reasons.append("Not a junction table")

            # Has unique identifier beyond just an ID
            unique_cols = [c for c in table.columns if c.is_unique and c.name not in ['id', 'uuid']]
            if unique_cols:
                score += 1
                reasons.append("Has unique business identifiers")

            candidates.append({
                'table_name': table.name,
                'entity_score': score,
                'reasons': reasons,
                'likely_entity': score >= 3
            })

        return sorted(candidates, key=lambda x: x['entity_score'], reverse=True)

    def _is_junction_table(self, table: Table) -> bool:
        """Determine if a table is a many-to-many junction table."""
        # Junction tables typically have:
        # - Composite primary key of 2+ foreign keys
        # - Few additional columns
        # - Name pattern like "table1_table2" or "table1_to_table2"

        fk_columns = [c for c in table.columns if c.is_foreign_key]
        non_fk_columns = [c for c in table.columns if not c.is_foreign_key and not c.is_primary_key]

        # Has 2+ foreign keys and few other columns
        if len(fk_columns) >= 2 and len(non_fk_columns) <= 2:
            return True

        # Check naming patterns
        junction_patterns = ['_to_', '_has_', '_x_', 'map_', 'link_']
        if any(pattern in table.name.lower() for pattern in junction_patterns):
            return True

        return False


class SchemaInspector:
    """Inspector for PostgreSQL database schemas."""

    def __init__(self, connection_string: str):
        """
        Initialize the schema inspector.

        Args:
            connection_string: PostgreSQL connection string
                (e.g., 'postgresql://user:pass@localhost/dbname')
        """
        self.connection_string = connection_string
        self.conn = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def connect(self):
        """Establish database connection."""
        self.conn = psycopg2.connect(self.connection_string)

    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def inspect(self, schemas: Optional[List[str]] = None,
                exclude_schemas: Optional[List[str]] = None,
                include_row_counts: bool = True) -> DatabaseSchema:
        """
        Inspect the database schema.

        Args:
            schemas: List of schema names to inspect (default: all except system schemas)
            exclude_schemas: List of schema names to exclude
            include_row_counts: Whether to count rows in each table

        Returns:
            DatabaseSchema object containing complete schema information
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Get database name
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()['current_database']

        # Get schemas
        all_schemas = self._get_schemas(cursor, schemas, exclude_schemas)

        # Get all tables
        tables = []
        for schema in all_schemas:
            schema_tables = self._get_tables(cursor, schema, include_row_counts)
            tables.extend(schema_tables)

        cursor.close()

        return DatabaseSchema(
            database_name=db_name,
            tables=tables,
            schemas=all_schemas
        )

    def _get_schemas(self, cursor, schemas: Optional[List[str]],
                     exclude_schemas: Optional[List[str]]) -> List[str]:
        """Get list of schemas to inspect."""
        if schemas:
            return schemas

        # Get all schemas except system schemas
        cursor.execute("""
                       SELECT schema_name
                       FROM information_schema.schemata
                       WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                       ORDER BY schema_name
                       """)

        all_schemas = [row['schema_name'] for row in cursor.fetchall()]

        if exclude_schemas:
            all_schemas = [s for s in all_schemas if s not in exclude_schemas]

        return all_schemas

    def _get_tables(self, cursor, schema: str, include_row_counts: bool) -> List[Table]:
        """Get all tables in a schema."""
        cursor.execute("""
                       SELECT table_name,
                              obj_description((quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass) as description
                       FROM information_schema.tables
                       WHERE table_schema = %s
                         AND table_type = 'BASE TABLE'
                       ORDER BY table_name
                       """, (schema,))

        tables = []
        for row in cursor.fetchall():
            table_name = row['table_name']
            table = Table(
                name=table_name,
                schema=schema,
                columns=self._get_columns(cursor, schema, table_name),
                primary_keys=self._get_primary_keys(cursor, schema, table_name),
                foreign_keys=self._get_foreign_keys(cursor, schema, table_name),
                indexes=self._get_indexes(cursor, schema, table_name),
                description=row['description']
            )

            if include_row_counts:
                table.row_count = self._get_row_count(cursor, schema, table_name)

            tables.append(table)

        return tables

    def _get_columns(self, cursor, schema: str, table_name: str) -> List[Column]:
        """Get all columns for a table."""
        cursor.execute("""
                       SELECT c.column_name,
                              c.data_type,
                              c.is_nullable,
                              c.character_maximum_length,
                              c.numeric_precision,
                              c.numeric_scale,
                              c.column_default,
                              col_description(
                                      (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass,
                                      c.ordinal_position) as description
                       FROM information_schema.columns c
                       WHERE c.table_schema = %s
                         AND c.table_name = %s
                       ORDER BY c.ordinal_position
                       """, (schema, table_name))

        columns = []
        primary_keys = set(self._get_primary_keys(cursor, schema, table_name))
        foreign_key_columns = set(self._get_foreign_key_columns(cursor, schema, table_name))
        unique_columns = set(self._get_unique_columns(cursor, schema, table_name))

        for row in cursor.fetchall():
            column = Column(
                name=row['column_name'],
                data_type=row['data_type'],
                is_nullable=row['is_nullable'] == 'YES',
                character_maximum_length=row['character_maximum_length'],
                numeric_precision=row['numeric_precision'],
                numeric_scale=row['numeric_scale'],
                column_default=row['column_default'],
                is_primary_key=row['column_name'] in primary_keys,
                is_foreign_key=row['column_name'] in foreign_key_columns,
                is_unique=row['column_name'] in unique_columns,
                description=row['description']
            )
            columns.append(column)

        return columns

    def _get_primary_keys(self, cursor, schema: str, table_name: str) -> List[str]:
        """Get primary key columns for a table."""
        cursor.execute("""
                       SELECT a.attname
                       FROM pg_index i
                                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY (i.indkey)
                       WHERE i.indrelid = (quote_ident(%s) || '.' || quote_ident(%s))::regclass
            AND i.indisprimary
                       """, (schema, table_name))

        return [row['attname'] for row in cursor.fetchall()]

    def _get_foreign_key_columns(self, cursor, schema: str, table_name: str) -> List[str]:
        """Get all columns that are part of foreign keys."""
        cursor.execute("""
                       SELECT kcu.column_name
                       FROM information_schema.table_constraints tc
                                JOIN information_schema.key_column_usage kcu
                                     ON tc.constraint_name = kcu.constraint_name
                                         AND tc.table_schema = kcu.table_schema
                       WHERE tc.constraint_type = 'FOREIGN KEY'
                         AND tc.table_schema = %s
                         AND tc.table_name = %s
                       """, (schema, table_name))

        return [row['column_name'] for row in cursor.fetchall()]

    def _get_unique_columns(self, cursor, schema: str, table_name: str) -> List[str]:
        """Get all columns with unique constraints."""
        cursor.execute("""
                       SELECT a.attname
                       FROM pg_index i
                                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY (i.indkey)
                       WHERE i.indrelid = (quote_ident(%s) || '.' || quote_ident(%s))::regclass
            AND i.indisunique
            AND NOT i.indisprimary
                       """, (schema, table_name))

        return [row['attname'] for row in cursor.fetchall()]

    def _get_foreign_keys(self, cursor, schema: str, table_name: str) -> List[ForeignKey]:
        """Get all foreign keys for a table."""
        cursor.execute("""
                       SELECT tc.constraint_name,
                              tc.table_schema,
                              tc.table_name,
                              kcu.column_name,
                              ccu.table_schema AS foreign_table_schema,
                              ccu.table_name   AS foreign_table_name,
                              ccu.column_name  AS foreign_column_name,
                              rc.delete_rule,
                              rc.update_rule
                       FROM information_schema.table_constraints AS tc
                                JOIN information_schema.key_column_usage AS kcu
                                     ON tc.constraint_name = kcu.constraint_name
                                         AND tc.table_schema = kcu.table_schema
                                JOIN information_schema.constraint_column_usage AS ccu
                                     ON ccu.constraint_name = tc.constraint_name
                                         AND ccu.table_schema = tc.table_schema
                                JOIN information_schema.referential_constraints AS rc
                                     ON tc.constraint_name = rc.constraint_name
                                         AND tc.table_schema = rc.constraint_schema
                       WHERE tc.constraint_type = 'FOREIGN KEY'
                         AND tc.table_schema = %s
                         AND tc.table_name = %s
                       ORDER BY tc.constraint_name, kcu.ordinal_position
                       """, (schema, table_name))

        # Group by constraint name
        fk_dict = defaultdict(lambda: {
            'source_columns': [],
            'target_columns': [],
            'on_delete': None,
            'on_update': None
        })

        for row in cursor.fetchall():
            constraint_name = row['constraint_name']
            fk_dict[constraint_name]['constraint_name'] = constraint_name
            fk_dict[constraint_name]['source_table'] = row['table_name']
            fk_dict[constraint_name]['target_table'] = row['foreign_table_name']
            fk_dict[constraint_name]['source_columns'].append(row['column_name'])
            fk_dict[constraint_name]['target_columns'].append(row['foreign_column_name'])
            fk_dict[constraint_name]['on_delete'] = row['delete_rule']
            fk_dict[constraint_name]['on_update'] = row['update_rule']

        return [ForeignKey(**fk_data) for fk_data in fk_dict.values()]

    def _get_indexes(self, cursor, schema: str, table_name: str) -> List[Index]:
        """Get all indexes for a table."""
        cursor.execute("""
                       SELECT i.relname                              AS index_name,
                              ix.indisunique                         AS is_unique,
                              ix.indisprimary                        AS is_primary,
                              am.amname                              AS index_type,
                              ARRAY_AGG(a.attname ORDER BY a.attnum) AS column_names
                       FROM pg_class t
                                JOIN pg_index ix ON t.oid = ix.indrelid
                                JOIN pg_class i ON i.oid = ix.indexrelid
                                JOIN pg_am am ON i.relam = am.oid
                                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY (ix.indkey)
                       WHERE t.relname = %s
                         AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
                       GROUP BY i.relname, ix.indisunique, ix.indisprimary, am.amname
                       ORDER BY i.relname
                       """, (table_name, schema))

        indexes = []
        for row in cursor.fetchall():
            index = Index(
                name=row['index_name'],
                table_name=table_name,
                columns=row['column_names'],
                is_unique=row['is_unique'],
                is_primary=row['is_primary'],
                index_type=row['index_type']
            )
            indexes.append(index)

        return indexes

    def _get_row_count(self, cursor, schema: str, table_name: str) -> int:
        """Get approximate row count for a table."""
        try:
            # Use statistics for fast approximate count
            cursor.execute("""
                           SELECT reltuples::bigint AS estimate
                           FROM pg_class
                           WHERE oid = (quote_ident(%s) || '.' || quote_ident(%s))::regclass
                           """, (schema, table_name))

            result = cursor.fetchone()
            return result['estimate'] if result else 0
        except Exception:
            return 0

    def get_schema_summary(self, schema: Optional[DatabaseSchema] = None) -> str:
        """
        Generate a human-readable summary of the schema.

        Args:
            schema: DatabaseSchema object (if None, will inspect the database)

        Returns:
            Formatted string summary
        """
        if schema is None:
            schema = self.inspect()

        summary = []
        summary.append(f"Database: {schema.database_name}")
        summary.append(f"Schemas: {', '.join(schema.schemas)}")
        summary.append(f"Total Tables: {len(schema.tables)}")
        summary.append("")

        for table in schema.tables:
            summary.append(f"Table: {table.schema}.{table.name}")
            if table.description:
                summary.append(f"  Description: {table.description}")
            if table.row_count is not None:
                summary.append(f"  Rows: {table.row_count:,}")
            summary.append(f"  Columns: {len(table.columns)}")
            summary.append(f"  Primary Keys: {', '.join(table.primary_keys) if table.primary_keys else 'None'}")
            summary.append(f"  Foreign Keys: {len(table.foreign_keys)}")
            summary.append(f"  Indexes: {len(table.indexes)}")
            summary.append("")

        return "\n".join(summary)


def main():
    """Example usage of the SchemaInspector."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python schema_inspector.py <connection_string>")
        print("Example: python schema_inspector.py 'postgresql://user:pass@localhost/dbname'")
        sys.exit(1)

    connection_string = sys.argv[1]

    with SchemaInspector(connection_string) as inspector:
        print("Inspecting database schema...")
        schema = inspector.inspect(include_row_counts=True)

        print("\n" + "=" * 80)
        print("SCHEMA SUMMARY")
        print("=" * 80)
        print(inspector.get_schema_summary(schema))

        print("\n" + "=" * 80)
        print("ENTITY CANDIDATES")
        print("=" * 80)
        for candidate in schema.get_entity_candidates():
            print(f"\nTable: {candidate['table_name']}")
            print(f"  Entity Score: {candidate['entity_score']}")
            print(f"  Likely Entity: {candidate['likely_entity']}")
            print(f"  Reasons: {', '.join(candidate['reasons'])}")

        print("\n" + "=" * 80)
        print("RELATIONSHIPS")
        print("=" * 80)
        for rel in schema.get_relationships():
            print(f"\n{rel['from_table']}.{','.join(rel['from_columns'])} -> "
                  f"{rel['to_table']}.{','.join(rel['to_columns'])}")
            print(f"  Cardinality: {rel['cardinality']}")

        # Optionally save to JSON
        output_file = "schema_output.json"
        with open(output_file, 'w') as f:
            f.write(schema.to_json())
        print(f"\n\nFull schema saved to: {output_file}")


if __name__ == "__main__":
    main()