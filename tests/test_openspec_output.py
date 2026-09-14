"""Reading OpenSpec's answers, over answers the real CLI actually gave.

The documents under `tests/fixtures/cli/` were captured from `openspec` 1.11.0 rather than
written by hand, so a shape that only exists in our imagination cannot pass these.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from specdeck.application.openspec import (
    ChangeList,
    SpecList,
    StatusReport,
    UnreadableAnswerError,
    ValidationReport,
    as_artifact,
    as_validation,
    not_a_root,
    read,
)
from specdeck.application.ports import CliOutput

CAPTURED = Path(__file__).resolve().parent / "fixtures" / "cli"


def answer(name: str, *, exit_code: int = 0) -> CliOutput:
    """What the CLI gave back that day, as it would arrive from the process."""
    document = json.loads((CAPTURED / f"{name}.json").read_text())
    return CliOutput(exit_code=exit_code, document=document)


def test_the_active_changes_are_read_with_their_counts() -> None:
    listing = read(answer("changes"), ChangeList)

    by_name = {change.name: change for change in listing.changes}
    assert set(by_name) == {"add-reminders", "retire-old-reports"}
    reminders = by_name["add-reminders"]
    assert (reminders.completed_tasks, reminders.total_tasks) == (1, 4)
    assert by_name["retire-old-reports"].status == "in-progress"
    assert reminders.last_modified is not None


def test_the_specs_are_read_with_their_requirement_counts() -> None:
    listing = read(answer("specs"), SpecList)

    assert {spec.id: spec.requirement_count for spec in listing.specs} == {
        "task-management": 2,
        "reports": 1,
    }


def test_the_pipeline_comes_from_the_schema_the_root_resolves() -> None:
    report = read(answer("status"), StatusReport)

    holed = next(
        change for change in report.changes if change.change_name == "retire-old-reports"
    )
    assert holed.schema_name == "spec-driven"
    assert not holed.is_complete

    # Status follows from whether a file exists, not from the order of the pipeline.
    by_id = {artifact.id: artifact for artifact in holed.artifacts}
    assert by_id["tasks"].status == "done"
    assert by_id["design"].status == "ready"
    assert as_artifact(by_id["tasks"]).requires == ("specs", "design")
    assert as_artifact(by_id["proposal"]).files == ("proposal.md",)


def test_a_green_root_still_carries_warnings_and_stays_valid() -> None:
    report = read(answer("validate"), ValidationReport)

    assert all(item.valid for item in report.items)

    verdicts = [as_validation(item) for item in report.items]
    assert sum(verdict.warnings for verdict in verdicts) > 0
    assert all(verdict.errors == 0 for verdict in verdicts)


def test_a_report_that_exited_one_is_read_in_full() -> None:
    # This is what `openspec validate` does when something is invalid: the whole report,
    # and a non-zero exit. Trusting the exit code would throw the report away.
    report = read(answer("validate-invalid", exit_code=1), ValidationReport)

    item = report.items[0]
    verdict = as_validation(item)

    assert not item.valid
    assert verdict.errors == 1
    assert verdict.warnings == 1
    assert "must include at least one scenario" in verdict.issues[1].message


def test_a_path_that_is_not_a_root_explains_itself_rather_than_failing() -> None:
    listing = read(answer("not-a-root", exit_code=1), ChangeList)

    assert listing.changes == ()
    assert not_a_root(listing) == "No OpenSpec root found from the current directory."


def test_a_root_that_is_one_has_nothing_to_explain() -> None:
    assert not_a_root(read(answer("changes"), ChangeList)) is None


def test_a_field_a_later_openspec_adds_is_ignored() -> None:
    document: dict[str, Any] = json.loads((CAPTURED / "changes.json").read_text())
    document["confidence"] = "high"
    document["changes"][0]["estimatedDays"] = 3

    listing = read(CliOutput(exit_code=0, document=document), ChangeList)

    assert len(listing.changes) == 2
    assert not hasattr(listing, "confidence")


def test_a_level_never_seen_before_is_shown_rather_than_hidden() -> None:
    report = read(
        CliOutput(
            exit_code=0,
            document={"items": [{"id": "x", "valid": True, "issues": [{"level": "FATAL"}]}]},
        ),
        ValidationReport,
    )
    verdict = as_validation(report.items[0])

    # Surfaced, and still not an error: whether the item is valid is the CLI's to say.
    assert verdict.warnings == 1
    assert verdict.errors == 0
    assert verdict.valid


def test_an_answer_that_was_not_json_is_said_rather_than_guessed_at() -> None:
    answered = CliOutput(exit_code=127, document=None, stderr="zsh: command not found")

    with pytest.raises(UnreadableAnswerError, match="no JSON document"):
        read(answered, ChangeList)
