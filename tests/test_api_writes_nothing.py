"""The API offers nothing that would write inside a registered repository.

The first hard rule of the product, checked against the contract the server actually
publishes rather than against anybody's memory of what was added. Whether a route writes to
a repository is not something a test can read off a document, so what is pinned here is the
whole set of operations that change anything at all: adding one fails this test, which is
the point. A new one is a decision, and it should cost a conversation.
"""

from pathlib import Path
from typing import Any

from specdeck.api.app import create_app

CHANGES_SOMETHING = {"post", "put", "patch", "delete"}

PERMITTED = {
    # The registry is under ~/.config/specdeck, which is the one path Specdeck writes to.
    ("post", "/api/repos"),
    ("delete", "/api/repos/{repo_id}"),
    # Reads a root again and replaces what is held in memory. Writes nothing anywhere.
    ("post", "/api/repos/{repo_id}/reading"),
}


def published() -> dict[str, Any]:
    return create_app(static_dir=Path("/no-interface-here")).openapi()


def test_the_only_operations_that_change_anything_are_the_permitted_ones() -> None:
    contract = published()

    changing = {
        (method, path)
        for path, operations in contract["paths"].items()
        for method in operations
        if method in CHANGES_SOMETHING
    }

    assert changing == PERMITTED


def test_everything_under_a_repository_is_read_only_bar_the_reading_itself() -> None:
    contract = published()

    under_a_repo = {
        (method, path)
        for path, operations in contract["paths"].items()
        for method in operations
        if path.startswith("/api/repos/{repo_id}/") and method in CHANGES_SOMETHING
    }

    assert under_a_repo == {("post", "/api/repos/{repo_id}/reading")}


def test_nothing_offers_to_archive_create_or_update_anything() -> None:
    # What OpenSpec's writing commands are called, in case one ever arrives by the back door.
    contract = published()

    written = " ".join(contract["paths"]).lower()

    assert not any(word in written for word in ("archive", "init", "update", "new", "apply"))
