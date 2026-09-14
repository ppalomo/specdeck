"""Everything Specdeck knows about one root after reading it."""

from datetime import datetime

from specdeck.domain.availability import Availability, Unreadable
from specdeck.domain.change import Change
from specdeck.domain.model import DomainModel
from specdeck.domain.repo import Repo
from specdeck.domain.spec import Spec


class Index(DomainModel):
    """The state of one root, read from disk and dated.

    `built_at` is part of what is known: while nothing watches the files, what is here and
    what is on disk drift apart, and the honest answer to "is this current?" is when it was
    read rather than a promise that it is.
    """

    repo: Repo
    schema_name: str | None = None
    """The schema the root resolves, which is what its changes' pipelines are drawn from."""

    specs: tuple[Spec, ...] = ()
    changes: tuple[Change, ...] = ()
    archived: tuple[Change, ...] = ()
    """Read from `openspec/changes/archive/`, because no OpenSpec command lists them."""

    canonical: Availability = Availability(available=True)
    """Whether the CLI could be asked. When it could not, validation and artifact status
    are missing from the changes above, and the rest of the index still stands."""

    unreadable: tuple[Unreadable, ...] = ()
    """Files that were there and could not be read. The rest of the root is here anyway."""

    built_at: datetime
