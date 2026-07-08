"""Tests for FormSubmissionRepository.

Responsibility:
- Verify all read and write operations on FormSubmissionRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from typing import Sequence
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FormSubmission
from app.repositories.forms.form_submission_repository import FormSubmissionRepository
from app.shared.enums import FormSubmissionStatus


FORM_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


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
def sample_submission() -> FormSubmission:
    """Return a deterministic FormSubmission instance for assertions."""
    return FormSubmission(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        form_id=FORM_ID,
        payload={"name": "Alice"},
        status=FormSubmissionStatus.PENDING,
    )


@pytest.fixture
def repository(mock_session: AsyncSession) -> FormSubmissionRepository:
    """Return a FormSubmissionRepository backed by the mocked session."""
    return FormSubmissionRepository(session=mock_session)


# TODO: add unit tests for logging assertions once they matter.
async def test_get_submission_by_id_found(
    repository: FormSubmissionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
    sample_submission: FormSubmission,
) -> None:
    """get(submission_id) should return the submission when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_submission
    mock_session.execute.return_value = mock_result

    submission = await repository.get(sample_submission.id)

    assert submission is sample_submission
    mock_session.execute.assert_awaited_once()


async def test_get_submission_by_id_not_found(
    repository: FormSubmissionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
) -> None:
    """get(submission_id) should return None when no submission matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    submission = await repository.get(uuid4())

    assert submission is None
    mock_session.execute.assert_awaited_once()


async def test_list_by_form_no_filter(
    repository: FormSubmissionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
    sample_submission: FormSubmission,
) -> None:
    """list_by_form without status filter should return all submissions for that form."""
    mock_result.scalars.return_value.all.return_value = [sample_submission]
    mock_session.execute.return_value = mock_result

    submissions: Sequence[FormSubmission] = await repository.list_by_form(FORM_ID)

    assert submissions == [sample_submission]
    mock_session.execute.assert_awaited_once()


async def test_list_by_form_with_status_filter(
    repository: FormSubmissionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
    sample_submission: FormSubmission,
) -> None:
    """list_by_form with status filter should narrow the results."""
    mock_result.scalars.return_value.all.return_value = [sample_submission]
    mock_session.execute.return_value = mock_result

    submissions = await repository.list_by_form(
        FORM_ID, status=FormSubmissionStatus.PENDING
    )

    assert submissions == [sample_submission]
    mock_session.execute.assert_awaited_once()


async def test_list_by_form_empty(
    repository: FormSubmissionRepository,
    mock_session: AsyncSession,
    mock_result: MagicMock,
) -> None:
    """list_by_form should return empty sequence when no submissions exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    submissions = await repository.list_by_form(uuid4())

    assert submissions == []
    mock_session.execute.assert_awaited_once()


async def test_create_submission(
    repository: FormSubmissionRepository,
    mock_session: AsyncSession,
    sample_submission: FormSubmission,
) -> None:
    """create(submission) should add, flush, refresh, and return the submission."""
    created = await repository.create(sample_submission)

    assert created is sample_submission
    mock_session.add.assert_called_once_with(sample_submission)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_submission)


async def test_delete_submission(
    repository: FormSubmissionRepository,
    mock_session: AsyncSession,
    sample_submission: FormSubmission,
) -> None:
    """delete(submission) should delete the submission, flush, and return it."""
    deleted = await repository.delete(sample_submission)

    assert deleted is sample_submission
    mock_session.delete.assert_awaited_once_with(sample_submission)
    mock_session.flush.assert_awaited_once()
