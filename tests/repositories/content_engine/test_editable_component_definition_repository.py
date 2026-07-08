"""Tests for EditableComponentDefinitionRepository.

Responsibility:
- Verify all read and write operations on EditableComponentDefinitionRepository
  using a mocked AsyncSession so the suite stays fast and isolated from the database.
"""

from typing import Sequence
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EditableComponentDefinition
from app.repositories.content_engine.editable_component_definition_repository import (
    EditableComponentDefinitionRepository,
)
from app.shared.enums import EditableComponentKind


SITE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
SOLUTION_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


@pytest.fixture
def mock_session() -> AsyncSession:
    """Return a mocked AsyncSession with all async methods pre-wired."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_result() -> MagicMock:
    """Return a MagicMock that mimics SQLAlchemy's Result object."""
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    scalar_result = MagicMock()
    scalar_result.all = MagicMock(return_value=[])
    result.scalars = MagicMock(return_value=scalar_result)
    return result


@pytest.fixture
def sample_definition() -> EditableComponentDefinition:
    """Return a deterministic EditableComponentDefinition instance for assertions."""
    return EditableComponentDefinition(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        site_id=SITE_ID,
        solution_id=SOLUTION_ID,
        key="hero",
        display_name="Hero",
        kind=EditableComponentKind.SINGLETON,
        display_order=0,
        editor_schema=[],
    )


@pytest.fixture
def repository(mock_session: AsyncSession) -> EditableComponentDefinitionRepository:
    """Return an EditableComponentDefinitionRepository backed by the mocked session."""
    return EditableComponentDefinitionRepository(session=mock_session)


# TODO: add unit tests for logging assertions once they matter.
async def test_get_definition_by_id_found(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
    sample_definition: EditableComponentDefinition,
) -> None:
    """get(definition_id) should return the definition when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_definition
    mock_session.execute.return_value = mock_result

    definition = await repository.get(sample_definition.id)

    assert definition is sample_definition
    mock_session.execute.assert_awaited_once()


async def test_get_definition_by_id_not_found(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
) -> None:
    """get(definition_id) should return None when no definition matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    definition = await repository.get(uuid4())

    assert definition is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_site_and_key_found(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
    sample_definition: EditableComponentDefinition,
) -> None:
    """get_by_site_and_key should return the definition with the matching key within a site."""
    mock_result.scalar_one_or_none.return_value = sample_definition
    mock_session.execute.return_value = mock_result

    definition = await repository.get_by_site_and_key(SITE_ID, "hero")

    assert definition is sample_definition
    mock_session.execute.assert_awaited_once()


async def test_get_by_site_and_key_not_found(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
) -> None:
    """get_by_site_and_key should return None when the key is unknown for that site."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    definition = await repository.get_by_site_and_key(SITE_ID, "nonexistent")

    assert definition is None
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_no_filter(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
    sample_definition: EditableComponentDefinition,
) -> None:
    """list_by_site without kind filter should return all definitions for that site."""
    mock_result.scalars.return_value.all.return_value = [sample_definition]
    mock_session.execute.return_value = mock_result

    definitions: Sequence[EditableComponentDefinition] = await repository.list_by_site(
        SITE_ID
    )

    assert definitions == [sample_definition]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_with_kind_filter(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
    sample_definition: EditableComponentDefinition,
) -> None:
    """list_by_site with kind filter should narrow the results."""
    mock_result.scalars.return_value.all.return_value = [sample_definition]
    mock_session.execute.return_value = mock_result

    definitions = await repository.list_by_site(
        SITE_ID, kind=EditableComponentKind.SINGLETON
    )

    assert definitions == [sample_definition]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_empty(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
) -> None:
    """list_by_site should return empty sequence when no definitions exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    definitions = await repository.list_by_site(uuid4())

    assert definitions == []
    mock_session.execute.assert_awaited_once()


async def test_create_definition(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    sample_definition: EditableComponentDefinition,
) -> None:
    """create(definition) should add, flush, refresh, and return the definition."""
    created = await repository.create(sample_definition)

    assert created is sample_definition
    mock_session.add.assert_called_once_with(sample_definition)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_definition)


async def test_delete_definition(
    repository: EditableComponentDefinitionRepository,
    mock_session: AsyncSession,
    sample_definition: EditableComponentDefinition,
) -> None:
    """delete(definition) should delete the definition, flush, and return it."""
    deleted = await repository.delete(sample_definition)

    assert deleted is sample_definition
    mock_session.delete.assert_awaited_once_with(sample_definition)
    mock_session.flush.assert_awaited_once()
