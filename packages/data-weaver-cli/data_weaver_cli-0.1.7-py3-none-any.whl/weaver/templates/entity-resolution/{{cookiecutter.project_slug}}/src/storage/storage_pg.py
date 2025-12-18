{% if cookiecutter.database == 'postgresql' -%}
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

Base = declarative_base()


class Entity(Base):
    """Example entity table for entity resolution."""
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    source = Column(String(100), nullable=False)
    confidence_score = Column(Integer, default=0)
    attributes = Column(Text)  # JSON string for additional attributes
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', type='{self.entity_type}')>"


class PostgreSQLStorage:
    """PostgreSQL storage implementation using SQLAlchemy."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def create_entity(self, name: str, entity_type: str, source: str,
                           confidence_score: int = 0, attributes: str = None) -> Entity:
        """Create a new entity."""
        async with self.async_session() as session:
            entity = Entity(
                name=name,
                entity_type=entity_type,
                source=source,
                confidence_score=confidence_score,
                attributes=attributes
            )
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def get_entity_by_id(self, entity_id: int) -> Optional[Entity]:
        """Get an entity by ID."""
        async with self.async_session() as session:
            result = await session.get(Entity, entity_id)
            return result

    async def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type."""
        from sqlalchemy import select

        async with self.async_session() as session:
            stmt = select(Entity).where(Entity.entity_type == entity_type)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def search_entities_by_name(self, name_pattern: str) -> List[Entity]:
        """Search entities by name pattern."""
        from sqlalchemy import select

        async with self.async_session() as session:
            stmt = select(Entity).where(Entity.name.ilike(f"%{name_pattern}%"))
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_entity(self, entity_id: int, **kwargs) -> Optional[Entity]:
        """Update an entity."""
        async with self.async_session() as session:
            entity = await session.get(Entity, entity_id)
            if entity:
                for key, value in kwargs.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                await session.commit()
                await session.refresh(entity)
            return entity

    async def mark_entity_resolved(self, entity_id: int) -> bool:
        """Mark an entity as resolved."""
        entity = await self.update_entity(entity_id, is_resolved=True)
        return entity is not None

    async def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity."""
        async with self.async_session() as session:
            entity = await session.get(Entity, entity_id)
            if entity:
                await session.delete(entity)
                await session.commit()
                return True
            return False

    async def get_unresolved_entities(self, limit: int = 100) -> List[Entity]:
        """Get unresolved entities."""
        from sqlalchemy import select

        async with self.async_session() as session:
            stmt = select(Entity).where(Entity.is_resolved == False).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def close(self):
        """Close the database connection."""
        await self.engine.dispose()


# Example usage
async def example_usage():
    """Example of how to use the PostgreSQL storage."""
    # Connection string format: postgresql+asyncpg://user:password@localhost/dbname
    storage = PostgreSQLStorage("postgresql+asyncpg://postgres:postgres@localhost/{{ cookiecutter.project_slug }}")

    try:
        # Create tables
        await storage.create_tables()

        # Create some entities
        entity1 = await storage.create_entity(
            name="John Smith",
            entity_type="person",
            source="database_a",
            confidence_score=85,
            attributes='{"age": 30, "city": "New York"}'
        )

        entity2 = await storage.create_entity(
            name="J. Smith",
            entity_type="person",
            source="database_b",
            confidence_score=70,
            attributes='{"occupation": "engineer"}'
        )

        # Search for entities
        similar_entities = await storage.search_entities_by_name("Smith")
        print(f"Found {len(similar_entities)} entities with 'Smith' in name")

        # Mark entity as resolved
        await storage.mark_entity_resolved(entity1.id)

        # Get unresolved entities
        unresolved = await storage.get_unresolved_entities()
        print(f"Found {len(unresolved)} unresolved entities")

    finally:
        await storage.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
{%- endif %}