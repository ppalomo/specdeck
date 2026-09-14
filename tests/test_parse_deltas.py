"""Reading a change's delta spec: which capability it touches and what it proposes to do."""

from pathlib import Path

from specdeck.domain.parsers.spec import parse_deltas, parse_spec

REMINDERS = "openspec/changes/add-reminders/specs/task-management/spec.md"
REPORTS = "openspec/changes/retire-old-reports/specs/reports/spec.md"
CURRENT = "openspec/specs/task-management/spec.md"


def test_a_delta_says_which_capability_and_which_operation(full_root: Path) -> None:
    deltas = parse_deltas(
        (full_root / REMINDERS).read_text(), capability="task-management", file=REMINDERS
    )

    assert [delta.operation for delta in deltas] == ["MODIFIED", "ADDED"]
    assert {delta.capability for delta in deltas} == {"task-management"}


def test_every_operation_is_recognised(full_root: Path) -> None:
    deltas = parse_deltas((full_root / REPORTS).read_text(), capability="reports", file=REPORTS)

    assert [delta.operation for delta in deltas] == ["MODIFIED", "REMOVED", "RENAMED"]


def test_a_rename_is_reported_even_though_it_states_no_requirement(full_root: Path) -> None:
    # A RENAMED section says what it says in FROM and TO lines. Reporting it only when it
    # holds a requirement heading would lose the edit entirely.
    deltas = parse_deltas((full_root / REPORTS).read_text(), capability="reports", file=REPORTS)
    renamed = next(delta for delta in deltas if delta.operation == "RENAMED")

    assert renamed.requirements == ()


def test_a_delta_keeps_the_scenarios_of_what_it_proposes(full_root: Path) -> None:
    deltas = parse_deltas(
        (full_root / REMINDERS).read_text(), capability="task-management", file=REMINDERS
    )
    added = next(delta for delta in deltas if delta.operation == "ADDED")

    assert added.requirements[0].name == "Una tarea puede avisar una vez"
    assert [scenario.name for scenario in added.requirements[0].scenarios] == [
        "La hora llega",
        "El envío se ejecuta otra vez",
    ]


def test_a_delta_is_not_the_current_spec_of_the_same_capability(full_root: Path) -> None:
    current = parse_spec((full_root / CURRENT).read_text(), id="task-management", file=CURRENT)
    deltas = parse_deltas(
        (full_root / REMINDERS).read_text(), capability="task-management", file=REMINDERS
    )
    modified = next(delta for delta in deltas if delta.operation == "MODIFIED")

    # Same requirement by name, and not the same thing: the delta proposes a scenario the
    # spec in force does not have, and says it is a MODIFIED rather than today's truth.
    in_force = current.requirements[0]
    proposed = modified.requirements[0]

    assert in_force.name == proposed.name
    assert len(in_force.scenarios) == 2
    assert len(proposed.scenarios) == 3
    assert proposed.scenarios[2].name == "Dar por hecha una tarea con recordatorio"


def test_a_delta_carries_no_purpose_because_only_a_capability_has_one(full_root: Path) -> None:
    # `parse_spec` over a delta would find no Purpose section; a delta is read as deltas.
    deltas = parse_deltas(
        (full_root / REMINDERS).read_text(), capability="task-management", file=REMINDERS
    )

    assert deltas
    assert all(delta.requirements is not None for delta in deltas)


def test_a_document_with_no_delta_sections_proposes_nothing() -> None:
    assert parse_deltas("## Purpose\n\nSólo esto.\n", capability="c", file="spec.md") == ()


def test_a_heading_that_only_looks_like_an_operation_is_not_one() -> None:
    source = "## ADDED Requirements for later\n\n### Requirement: X\n\nTexto.\n"

    assert parse_deltas(source, capability="c", file="spec.md") == ()
