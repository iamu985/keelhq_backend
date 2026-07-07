"""Form submission repository.

Responsibility:
- Provide all database read and write operations for the FormSubmission model.
- Remain free of business logic and exception handling.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.logger import logger
from app.db.models import FormSubmission
from app.shared.enums import FormSubmissionStatus


# TODO: add unit tests for this repository
class FormSubmissionRepository:
    """Data access layer for the FormSubmission model.

    Responsibility:
    - Execute parameterised SQL queries against the form_submissions table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, submission_id: UUID) -> Optional[FormSubmission]:
        """Return the submission with the given primary key, or None if not found."""
        logger.info("Fetching FormSubmission by id.")
        logger.debug(f"submission_id={submission_id}")

        stmt = select(FormSubmission).where(FormSubmission.id == submission_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_form(
        self,
        form_id: UUID,
        status: Optional[FormSubmissionStatus] = None,
    ) -> Sequence[FormSubmission]:
        """Return all submissions for a form, with optional status filter."""
        logger.info("Listing FormSubmissions by form_id.")
        logger.debug(f"form_id={form_id} status={status}")

        stmt = select(FormSubmission).where(FormSubmission.form_id == form_id)
        if status is not None:
            stmt = stmt.where(FormSubmission.status == status)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, submission: FormSubmission) -> FormSubmission:
        """Persist a new FormSubmission and return the refreshed instance."""
        logger.info("Creating FormSubmission.")
        logger.debug(f"form_id={submission.form_id}")

        self.session.add(submission)
        await self.session.flush()
        await self.session.refresh(submission)
        return submission

    async def delete(self, submission: FormSubmission) -> FormSubmission:
        """Delete the given FormSubmission and return the deleted instance."""
        logger.info("Deleting FormSubmission.")
        logger.debug(f"submission_id={submission.id}")

        await self.session.delete(submission)
        await self.session.flush()
        return submission
