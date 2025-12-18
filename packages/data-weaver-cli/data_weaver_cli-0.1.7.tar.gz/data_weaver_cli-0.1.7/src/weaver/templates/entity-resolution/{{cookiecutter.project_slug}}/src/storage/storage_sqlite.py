{% if cookiecutter.database == 'sqlite' -%}
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

class Entity(SQLModel, table=True):
    """Example entity table for entity resolution using SQLModel."""
    __tablename__ = "entities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    entity_type: str = Field(max_length=100)
    source: str = Field(max_length=100)
    confidence_score: int = Field(default=0)
    attributes: Optional[str] = Field(default=None)  # JSON string for additional attributes
    is_resolved: bool = Field(default=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', type='{self.entity_type}')>"


class SQLiteStorage:
    """SQLite storage implementation using SQLModel."""

    def __init__(self, database_path: str = "{{ cookiecutter.project_slug }}.db"):
        # For async SQLite, use aiosqlite
        self.database_url = f"sqlite+aiosqlite:///{database_path}"
        self.sync_database_url = f"sqlite:///{database_path}"

        # Async engine for async operations
        self.async_engine = create_async_engine(
            self.database_url,
            echo=True,
            connect_args={"check_same_thread": False}
        )

        # Sync engine for table creation
        self.sync_engine = create_engine(
            self.sync_database_url,
            echo=True,
            connect_args={"check_same_thread": False}
        )

    def create_tables(self):
        """Create all tables (synchronous)."""
        SQLModel.metadata.create_all(self.sync_engine)

    def drop_tables(self):
        """Drop all tables (synchronous)."""
        SQLModel.metadata.drop_all(self.sync_engine)

    async def create_entity(self, name: str, entity_type: str, source: str,
                           confidence_score: int = 0, attributes: str = None) -> Entity:
        """Create a new entity."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            entity = Entity(
                name=name,
                entity_type=entity_type,
                source=source,
                confidence_score=confidence_score,
                attributes=attributes,
                created_at=datetime.now()
            )
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def get_entity_by_id(self, entity_id: int) -> Optional[Entity]:
        """Get an entity by ID."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            return await session.get(Entity, entity_id)

    async def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            statement = select(Entity).where(Entity.entity_type == entity_type)
            result = await session.exec(statement)
            return list(result.all())

    async def search_entities_by_name(self, name_pattern: str) -> List[Entity]:
        """Search entities by name pattern."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            statement = select(Entity).where(Entity.name.contains(name_pattern))
            result = await session.exec(statement)
            return list(result.all())

    async def update_entity(self, entity_id: int, **kwargs) -> Optional[Entity]:
        """Update an entity."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            entity = await session.get(Entity, entity_id)
            if entity:
                for key, value in kwargs.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                entity.updated_at = datetime.now()
                session.add(entity)
                await session.commit()
                await session.refresh(entity)
            return entity

    async def mark_entity_resolved(self, entity_id: int) -> bool:
        """Mark an entity as resolved."""
        entity = await self.update_entity(entity_id, is_resolved=True)
        return entity is not None

    async def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            entity = await session.get(Entity, entity_id)
            if entity:
                await session.delete(entity)
                await session.commit()
                return True
            return False

    async def get_unresolved_entities(self, limit: int = 100) -> List[Entity]:
        """Get unresolved entities."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            statement = select(Entity).where(Entity.is_resolved == False).limit(limit)
            result = await session.exec(statement)
            return list(result.all())

    async def get_entities_by_confidence_range(self, min_score: int, max_score: int) -> List[Entity]:
        """Get entities within a confidence score range."""
        async with SQLModelAsyncSession(self.async_engine) as session:
            statement = select(Entity).where(
                Entity.confidence_score >= min_score,
                Entity.confidence_score <= max_score
            )
            result = await session.exec(statement)
            return list(result.all())

    async def close(self):
        """Close the database connection."""
        await self.async_engine.dispose()

    # Synchronous methods for simple operations
    def create_entity_sync(self, name: str, entity_type: str, source: str,
                          confidence_score: int = 0, attributes: str = None) -> Entity:
        """Create a new entity (synchronous)."""
        with Session(self.sync_engine) as session:
            entity = Entity(
                name=name,
                entity_type=entity_type,
                source=source,
                confidence_score=confidence_score,
                attributes=attributes,
                created_at=datetime.now()
            )
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity

    def get_all_entities_sync(self) -> List[Entity]:
        """Get all entities (synchronous)."""
        with Session(self.sync_engine) as session:
            statement = select(Entity)
            result = session.exec(statement)
            return list(result.all())


# Example usage
async def example_usage():
    """Example of how to use the SQLite storage."""
    storage = SQLiteStorage("example_entities.db")

    try:
        # Create tables
        storage.create_tables()

        # Create some entities
        entity1 = await storage.create_entity(
            name="Alice Johnson",
            entity_type="person",
            source="csv_import",
            confidence_score=90,
            attributes='{"age": 28, "department": "Engineering"}'
        )

        entity2 = await storage.create_entity(
            name="A. Johnson",
            entity_type="person",
            source="email_extraction",
            confidence_score=75,
            attributes='{"email": "a.johnson@company.com"}'
        )

        entity3 = await storage.create_entity(
            name="Apple Inc.",
            entity_type="company",
            source="web_scraping",
            confidence_score=95,
            attributes='{"industry": "Technology", "founded": 1976}'
        )

        # Search for entities
        people = await storage.get_entities_by_type("person")
        print(f"Found {len(people)} person entities")

        johnson_entities = await storage.search_entities_by_name("Johnson")
        print(f"Found {len(johnson_entities)} entities with 'Johnson' in name")

        # Get entities by confidence range
        high_confidence = await storage.get_entities_by_confidence_range(80, 100)
        print(f"Found {len(high_confidence)} high-confidence entities")

        # Mark entity as resolved
        await storage.mark_entity_resolved(entity1.id)

        # Get unresolved entities
        unresolved = await storage.get_unresolved_entities()
        print(f"Found {len(unresolved)} unresolved entities")

        # Synchronous example
        sync_entity = storage.create_entity_sync(
            name="Bob Smith",
            entity_type="person",
            source="manual_entry",
            confidence_score=100
        )
        print(f"Created entity synchronously: {sync_entity}")

    finally:
        await storage.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
{%- endif %}