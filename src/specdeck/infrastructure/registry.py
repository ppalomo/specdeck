"""The registry on disk: the only file Specdeck writes."""

import json
from collections.abc import Sequence
from pathlib import Path

from specdeck.domain.repo import Repo

VERSION = 1

# Where the registry lives. Under the user's configuration rather than beside the working
# directory, so which roots are registered does not depend on where Specdeck was started.
DEFAULT_PATH = Path.home() / ".config" / "specdeck" / "repos.json"


class JsonRegistryStore:
    """The registered roots, as a JSON file a person can read and repair.

    Not a database: this is configuration. It is a handful of entries, it is edited by hand
    when something goes wrong, and it fits on a screen.
    """

    def __init__(self, path: Path | None = None) -> None:
        """Keep the registry at the given path, the user's configuration by default.

        The default is read here rather than bound to the signature, so that a test can
        point the whole product at a registry of its own without going near the one
        belonging to whoever is running it.
        """
        self.path = path if path is not None else DEFAULT_PATH

    def load(self) -> tuple[Repo, ...]:
        """Read the registered roots. An absent store reads as none registered."""
        if not self.path.is_file():
            return ()

        written = json.loads(self.path.read_text(encoding="utf-8"))
        return tuple(Repo.model_validate(entry) for entry in written.get("repos", []))

    def save(self, repos: Sequence[Repo]) -> None:
        """Write the registered roots, atomically.

        Through a temporary file in the same directory and a rename, which the filesystem
        performs in one step. A crash halfway leaves the previous registry whole rather than
        a truncated file that no longer parses — and losing the list of registered roots to
        a power cut is the kind of small betrayal that is never forgiven.
        """
        written = json.dumps(
            {
                "version": VERSION,
                # Availability is what the machine is like right now, not what was decided.
                # It is worked out again on every read, so it is not written down.
                "repos": [
                    repo.model_dump(mode="json", exclude={"availability"}) for repo in repos
                ],
            },
            indent=2,
            ensure_ascii=False,
        )

        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f"{self.path.name}.writing")
        try:
            temporary.write_text(f"{written}\n", encoding="utf-8")
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)
