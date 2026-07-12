"""Tests for SolutionRepository.

Responsibility:
- Verify all read and write operations on SolutionRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keelhq.db.models import Solution
from keelhq.repositories.site_management.solution_repository import SolutionRepository
from keelhq.schemas.site_management.solution_schemas import ListSolutionQuery


@pytest.fixture
def mock_session() -> AsyncMock:
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
def sample_solution() -> Solution:
    """Return a deterministic Solution instance for assertions."""
    return Solution(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        name="business",
        slug="business",
        display_name="Business",
        version="0.1.0",
        is_builtin=True,
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> SolutionRepository:
    """Return a SolutionRepository backed by the mocked session."""
    return SolutionRepository(session=cast(AsyncSession, mock_session))


# TODO: add unit tests for logging assertions once they matter.
async def test_get_solution_by_id_found(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_solution: Solution,
) -> None:
    """get(solution_id) should return the solution when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_solution
    mock_session.execute.return_value = mock_result

    solution = await repository.get(sample_solution.id)

    assert solution is sample_solution
    mock_session.execute.assert_awaited_once()


async def test_get_solution_by_id_not_found(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(solution_id) should return None when no solution matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    solution = await repository.get(uuid4())

    assert solution is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_slug_found(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_solution: Solution,
) -> None:
    """get_by_slug(slug) should return the solution with a matching slug."""
    mock_result.scalar_one_or_none.return_value = sample_solution
    mock_session.execute.return_value = mock_result

    solution = await repository.get_by_slug("business")

    assert solution is sample_solution
    mock_session.execute.assert_awaited_once()


async def test_get_by_slug_not_found(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_slug(slug) should return None when the slug is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    solution = await repository.get_by_slug("nonexistent")

    assert solution is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_name_found(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_solution: Solution,
) -> None:
    """get_by_name(name) should return the solution with a matching name."""
    mock_result.scalar_one_or_none.return_value = sample_solution
    mock_session.execute.return_value = mock_result

    solution = await repository.get_by_name("business")

    assert solution is sample_solution
    mock_session.execute.assert_awaited_once()


async def test_get_by_name_not_found(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_name(name) should return None when the name is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    solution = await repository.get_by_name("nonexistent")

    assert solution is None
    mock_session.execute.assert_awaited_once()


async def test_create_solution(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    sample_solution: Solution,
) -> None:
    """create(solution) should add, flush, refresh, and return the solution."""
    created = await repository.create(sample_solution)

    assert created is sample_solution
    mock_session.add.assert_called_once_with(sample_solution)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_solution)


async def test_list_solutions_no_query(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_solution: Solution,
) -> None:
    """list(None) should return all solutions without any filter."""
    mock_result.scalars.return_value.all.return_value = [sample_solution]
    mock_session.execute.return_value = mock_result

    solutions = await repository.list()

    assert solutions == [sample_solution]
    mock_session.execute.assert_awaited_once()


async def test_list_solutions_builtin_filter(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_solution: Solution,
) -> None:
    """list(query) should apply is_builtin filter when provided."""
    mock_result.scalars.return_value.all.return_value = [sample_solution]
    mock_session.execute.return_value = mock_result

    query = ListSolutionQuery(is_builtin=True)
    solutions = await repository.list(query=query)

    assert solutions == [sample_solution]
    mock_session.execute.assert_awaited_once()


async def test_list_solutions_empty(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list() should return an empty sequence when no solutions exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    solutions = await repository.list()

    assert solutions == []
    mock_session.execute.assert_awaited_once()


async def test_delete_solution(
    repository: SolutionRepository,
    mock_session: AsyncMock,
    sample_solution: Solution,
) -> None:
    """delete(solution) should delete the solution, flush, and return it."""
    deleted = await repository.delete(sample_solution)

    assert deleted is sample_solution
    mock_session.delete.assert_awaited_once_with(sample_solution)
    mock_session.flush.assert_awaited_once()
