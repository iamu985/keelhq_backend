"""Tests for FormRepository.

Responsibility:
- Verify all read and write operations on FormRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from collections.abc import Sequence
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keelhq.db.models import Form
from keelhq.repositories.forms.form_repository import FormRepository

SITE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


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
def sample_form() -> Form:
    """Return a deterministic Form instance for assertions."""
    return Form(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        site_id=SITE_ID,
        name="Contact Form",
        slug="contact",
        field_schema=[],
        settings={},
        is_active=True,
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> FormRepository:
    """Return a FormRepository backed by the mocked session."""
    return FormRepository(session=cast(AsyncSession, mock_session))


# TODO: add unit tests for logging assertions once they matter.
async def test_get_form_by_id_found(
    repository: FormRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_form: Form,
) -> None:
    """get(form_id) should return the form when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_form
    mock_session.execute.return_value = mock_result

    form = await repository.get(sample_form.id)

    assert form is sample_form
    mock_session.execute.assert_awaited_once()


async def test_get_form_by_id_not_found(
    repository: FormRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(form_id) should return None when no form matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    form = await repository.get(uuid4())

    assert form is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_site_and_slug_found(
    repository: FormRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_form: Form,
) -> None:
    """get_by_site_and_slug should return the form with the matching slug within a site."""
    mock_result.scalar_one_or_none.return_value = sample_form
    mock_session.execute.return_value = mock_result

    form = await repository.get_by_site_and_slug(SITE_ID, "contact")

    assert form is sample_form
    mock_session.execute.assert_awaited_once()


async def test_get_by_site_and_slug_not_found(
    repository: FormRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_site_and_slug should return None when the slug is unknown for that site."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    form = await repository.get_by_site_and_slug(SITE_ID, "nonexistent")

    assert form is None
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_no_filter(
    repository: FormRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_form: Form,
) -> None:
    """list_by_site without is_active filter should return all forms for that site."""
    mock_result.scalars.return_value.all.return_value = [sample_form]
    mock_session.execute.return_value = mock_result

    forms: Sequence[Form] = await repository.list_by_site(SITE_ID)

    assert forms == [sample_form]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_active_only(
    repository: FormRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_form: Form,
) -> None:
    """list_by_site with is_active=True should return only active forms."""
    mock_result.scalars.return_value.all.return_value = [sample_form]
    mock_session.execute.return_value = mock_result

    forms = await repository.list_by_site(SITE_ID, is_active=True)

    assert forms == [sample_form]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_empty(
    repository: FormRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list_by_site should return empty sequence when no forms exist for the site."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    forms = await repository.list_by_site(uuid4())

    assert forms == []
    mock_session.execute.assert_awaited_once()


async def test_create_form(
    repository: FormRepository,
    mock_session: AsyncMock,
    sample_form: Form,
) -> None:
    """create(form) should add, flush, refresh, and return the form."""
    created = await repository.create(sample_form)

    assert created is sample_form
    mock_session.add.assert_called_once_with(sample_form)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_form)


async def test_delete_form(
    repository: FormRepository,
    mock_session: AsyncMock,
    sample_form: Form,
) -> None:
    """delete(form) should delete the form, flush, and return it."""
    deleted = await repository.delete(sample_form)

    assert deleted is sample_form
    mock_session.delete.assert_awaited_once_with(sample_form)
    mock_session.flush.assert_awaited_once()
