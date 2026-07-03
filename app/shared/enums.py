"""Shared domain enumerations.

Responsibility:
- Provide strongly-typed values for the Content Engine domain.

These enums are used by both the dashboard generation layer and the database
schema. They are intentionally simple `str` enums so they serialize cleanly to
PostgreSQL and to JSON without surprising callers.
"""

from enum import Enum


class EditableComponentKind(str, Enum):
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


class ContentStatus(str, Enum):
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
