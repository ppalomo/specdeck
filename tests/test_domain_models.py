"""The domain models: what they compute, what they refuse, and how they serialize."""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from specdeck.domain.availability import Availability
from specdeck.domain.change import Artifact, Change, Task, TaskGroup, Tasks
from specdeck.domain.index import Index
from specdeck.domain.location import Location
from specdeck.domain.repo import Repo
from specdeck.domain.spec import Delta, Requirement, Scenario, Spec
from specdeck.domain.validation import Issue, Validation


def a_location(line: int = 1, file: str = "openspec/changes/c/tasks.md") -> Location:
    return Location(file=file, line=line)


def a_task(*, number: str, done: bool, line: int) -> Task:
    return Task(number=number, text=f"task {number}", done=done, location=a_location(line))


def test_tasks_count_what_is_done_across_every_group() -> None:
    tasks = Tasks(
        groups=(
            TaskGroup(
                title="1. First",
                location=a_location(1),
                tasks=(
                    a_task(number="1.1", done=True, line=3),
                    a_task(number="1.2", done=False, line=4),
                ),
            ),
            TaskGroup(
                title="2. Second",
                location=a_location(6),
                tasks=(a_task(number="2.1", done=True, line=8),),
            ),
        )
    )

    assert tasks.total == 3
    assert tasks.done == 2


def test_a_change_with_no_tasks_counts_zero_rather_than_failing() -> None:
    assert Tasks().total == 0
    assert Tasks().done == 0


def test_validation_keeps_the_levels_apart() -> None:
    validation = Validation(
        valid=True,
        issues=(
            Issue(level="WARNING", path="specs/a/spec.md", message="should contain SHALL"),
            Issue(level="WARNING", path="specs/b/spec.md", message="should contain SHALL"),
            Issue(level="INFO", path="specs/a/spec.md", message="requirement text is long"),
        ),
    )

    # Three issues, no errors: the item is valid, which a single count would have hidden.
    assert validation.valid
    assert validation.errors == 0
    assert validation.warnings == 2
    assert len(validation.issues) == 3


def test_a_spec_counts_its_own_requirements() -> None:
    spec = Spec(
        id="local-server",
        purpose="What the server is while it runs.",
        requirements=(
            Requirement(
                name="El servidor escucha solo en el bucle local",
                text="El servidor SHALL escuchar en 127.0.0.1.",
                location=a_location(10, "openspec/specs/local-server/spec.md"),
                scenarios=(
                    Scenario(
                        name="El servidor arranca",
                        location=a_location(20, "openspec/specs/local-server/spec.md"),
                        steps=("**WHEN** se arranca", "**THEN** queda escuchando"),
                    ),
                ),
            ),
        ),
    )

    assert spec.requirement_count == 1
    assert spec.requirements[0].scenarios[0].steps[1].endswith("queda escuchando")


def test_the_domain_is_frozen_because_it_is_a_cache_of_the_files() -> None:
    task = a_task(number="1.1", done=False, line=3)

    with pytest.raises(ValidationError):
        task.done = True  # pyright: ignore[reportAttributeAccessIssue]


def test_a_field_openspec_grows_later_is_ignored_rather_than_fatal() -> None:
    artifact = Artifact.model_validate(
        {"id": "tasks", "status": "done", "requires": ["specs"], "confidence": "high"}
    )

    assert artifact.id == "tasks"
    assert artifact.requires == ("specs",)
    assert not hasattr(artifact, "confidence")


def test_an_unknown_artifact_status_is_refused() -> None:
    with pytest.raises(ValidationError):
        Artifact.model_validate({"id": "tasks", "status": "nearly"})


def test_availability_says_why_when_something_could_not_be_read() -> None:
    missing = Availability.missing("the path no longer exists")

    assert not missing.available
    assert missing.reason == "the path no longer exists"
    assert Availability.present().reason is None


def test_an_index_serializes_to_what_the_api_will_publish() -> None:
    index = Index(
        repo=Repo(
            id="specdeck-a1b2",
            name="specdeck",
            path=Path("/Users/someone/Developer/specdeck"),
            kind="repo",
        ),
        schema_name="spec-driven",
        specs=(Spec(id="local-server"),),
        changes=(
            Change(
                id="index-openspec",
                status="in-progress",
                schema_name="spec-driven",
                artifacts=(Artifact(id="tasks", status="done", requires=("specs", "design")),),
                tasks=Tasks(
                    groups=(
                        TaskGroup(
                            title="1. Las capas",
                            location=a_location(1),
                            tasks=(a_task(number="1.1", done=True, line=3),),
                        ),
                    )
                ),
                deltas=(Delta(capability="local-server", operation="ADDED"),),
                validation=Validation(valid=True),
                last_modified=datetime(2026, 9, 14, 9, 0, tzinfo=UTC),
            ),
        ),
        archived=(
            Change(
                id="bootstrap-skeleton",
                status="archived",
                archived_on=date(2026, 9, 14),
            ),
        ),
        built_at=datetime(2026, 9, 14, 9, 30, tzinfo=UTC),
    )

    published = index.model_dump(mode="json")

    assert published["repo"]["path"] == "/Users/someone/Developer/specdeck"
    assert published["specs"][0]["requirement_count"] == 0
    assert published["changes"][0]["tasks"] == {
        "groups": published["changes"][0]["tasks"]["groups"],
        "total": 1,
        "done": 1,
    }
    assert published["changes"][0]["deltas"][0]["operation"] == "ADDED"
    assert published["archived"][0]["archived_on"] == "2026-09-14"
    assert published["canonical"] == {"available": True, "reason": None}
    assert published["built_at"] == "2026-09-14T09:30:00Z"


def test_a_root_whose_cli_could_not_be_asked_still_has_an_index() -> None:
    index = Index(
        repo=Repo(id="r", name="r", path=Path("/somewhere/r"), kind="store"),
        changes=(Change(id="c", status="planning"),),
        canonical=Availability.missing("the openspec executable is not installed"),
        built_at=datetime(2026, 9, 14, tzinfo=UTC),
    )

    assert index.changes[0].validation is None
    assert not index.canonical.available
    assert index.canonical.reason is not None
