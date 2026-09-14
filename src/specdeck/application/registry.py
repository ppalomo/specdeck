"""Registering the roots Specdeck watches, and keeping that list honest."""

import hashlib
import re
from pathlib import Path

from specdeck.application.ports import RegistryStore
from specdeck.domain.availability import Availability
from specdeck.domain.repo import Repo, RepoKind

CONFIG = Path("openspec") / "config.yaml"
"""What makes a directory a root. Nothing else is looked at to decide."""

STORE_MARKER = Path(".openspec-store") / "store.yaml"
"""What makes a root a store rather than one inside a code repository."""

NOT_WORD = re.compile(r"[^a-z0-9]+")


class NotAnOpenSpecRootError(Exception):
    """A path was offered for registration and there is no OpenSpec root there."""

    def __init__(self, path: Path) -> None:
        """Say which path was tried and what was expected to be in it."""
        self.path = path
        self.expected = path / CONFIG
        message = (
            f"{path} is not an OpenSpec root: there is no {self.expected} to read. "
            f"Register the directory that holds the openspec/ directory, not the openspec/ "
            f"directory itself."
        )
        super().__init__(message)


class NotRegisteredError(Exception):
    """Something was asked of a repository that is not in the registry."""

    def __init__(self, repo_id: str) -> None:
        """Say which identifier was asked for."""
        self.repo_id = repo_id
        message = f"No repository is registered as {repo_id!r}."
        super().__init__(message)


class Registry:
    """The roots Specdeck was told to watch.

    Registration is manual and by path: Specdeck never goes looking through the disk for
    roots it was not told about.

    The three questions about a path — does it exist, does it hold `openspec/config.yaml`,
    does it hold the store marker — are asked of the filesystem directly rather than through
    a port. The cases worth testing are a symlink, a `~`, a relative path and a directory
    that has gone, and every one of them only means something against a real filesystem: a
    port here would swap the thing under test for a fiction.
    """

    def __init__(self, store: RegistryStore) -> None:
        """Work over the given store, which is the only thing this writes to."""
        self._store = store

    def repos(self) -> tuple[Repo, ...]:
        """Every registered root, each with how it is doing right now."""
        return tuple(_as_it_is_now(repo) for repo in self._store.load())

    def add(self, path: Path) -> Repo:
        """Register a root by its path, or refuse saying what was looked for and where."""
        root = _resolved(path)
        if not (root / CONFIG).is_file():
            raise NotAnOpenSpecRootError(root)

        registered = self._store.load()
        already = next((repo for repo in registered if repo.path == root), None)
        if already is not None:
            # The same root reached another way is the root it already is.
            return _as_it_is_now(already)

        repo = Repo(id=_identity(root), name=root.name, path=root, kind=_kind(root))
        self._store.save([*registered, repo])
        return repo

    def remove(self, repo_id: str) -> Repo:
        """Take a root out of the registry. Nothing inside the root is touched."""
        registered = self._store.load()
        leaving = next((repo for repo in registered if repo.id == repo_id), None)
        if leaving is None:
            raise NotRegisteredError(repo_id)

        self._store.save([repo for repo in registered if repo.id != repo_id])
        return leaving


def _resolved(path: Path) -> Path:
    """Resolve a path to its one true form: absolute, `~` expanded, symlinks followed."""
    return path.expanduser().resolve()


def _kind(root: Path) -> RepoKind:
    """Whether the root stands on its own or sits inside a code repository."""
    return "store" if (root / STORE_MARKER).is_file() else "repo"


def _identity(root: Path) -> str:
    """Derive a name a person can read, made unique by where the root actually is.

    Two checkouts of the same project, or two directories both called `web`, are ordinary.
    The suffix is of the path, so it is stable across runs and machines-with-the-same-layout
    without a counter that would renumber everything the moment one is removed.
    """
    digest = hashlib.blake2s(str(root).encode(), digest_size=3).hexdigest()
    return f"{NOT_WORD.sub('-', root.name.lower()).strip('-') or 'root'}-{digest}"


def _as_it_is_now(repo: Repo) -> Repo:
    """Answer, for today, whether the registered root can be read.

    A root that is gone stays registered. An unplugged disk and a branch where the directory
    does not exist yet are both temporary, and dropping the entry over either would throw
    away a decision somebody made.
    """
    return repo.model_copy(update={"availability": _availability(repo.path)})


def _availability(path: Path) -> Availability:
    if not path.exists():
        return Availability.missing("the path no longer exists")
    if not path.is_dir():
        return Availability.missing("the path is no longer a directory")
    if not (path / CONFIG).is_file():
        return Availability.missing(f"there is no longer a {CONFIG} to read there")
    return Availability.present()
