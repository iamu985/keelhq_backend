"""Shared domain enumerations.

Responsibility:
- Provide strongly-typed values for the Content Engine domain.

These enums are used by both the dashboard generation layer and the database
schema. They are intentionally simple `str` enums so they serialize cleanly to
PostgreSQL and to JSON without surprising callers.
"""

from enum import StrEnum


class SiteVisibility(StrEnum):
    """
    Classification of Site's visibility.

    Responsibility:
    - Tell user and the dashboard/backend who can see the site.
    """

    PUBLIC = "public"
    """
    Site is public and everyone can visit the site.
    """

    PRIVATE = "private"
    """Site is private and requires authentication or role/permission"""

    UNLISTED = "unlisted"
    """Site is visible only to the people who has access to the private link"""


class SiteStatus(StrEnum):
    """
    Classification of Site's Status
    """

    DRAFT = "draft"
    """Site is still in development phase"""

    ACTIVE = "active"
    """Site is now active and can be used."""

    SUSPENDED = "suspended"
    """Site is disabled by owner/admin"""

    ARCHIVED = "archived"
    """Site is archived for history"""

    DELETED = "deleted"
    """Site is deleted by the owner or admin - soft delete"""


class EditableComponentKind(StrEnum):
    """Classification of an editable component's cardinality.

    Responsibility:
    - Tell the dashboard and backend whether a component expects exactly one
      entry or an arbitrary number of entries.
    """

    SINGLETON = "singleton"
    """Exactly one editable entry exists for this component.

    Examples: Hero, Footer, About, SEO.
    """

    COLLECTION = "collection"
    """Zero or more editable entries may exist for this component.

    Examples: Projects, Products, Services, Testimonials, FAQ.
    """


class ContentStatus(StrEnum):
    """Publication state of a content entry.

    Responsibility:
    - Control whether a content entry is visible to the frontend.
    """

    DRAFT = "draft"
    """Entry is being edited and should not be served publicly."""

    PUBLISHED = "published"
    """Entry is approved and may be served publicly."""

    ARCHIVED = "archived"
    """Entry is no longer published but is retained for history."""


class FormSubmissionStatus(StrEnum):
    """Processing state of a form submission.

    Responsibility:
    - Track whether a submission has been reviewed or flagged.
    """

    PENDING = "pending"
    """Submission has been received but not yet reviewed."""

    PROCESSED = "processed"
    """Submission has been reviewed and handled."""

    SPAM = "spam"
    """Submission was flagged as unsolicited or abusive."""
