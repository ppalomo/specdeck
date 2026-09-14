"""Reading `spec.md`: the purpose, the requirements, their scenarios and their lines."""

from pathlib import Path

from specdeck.domain.parsers.spec import parse_spec

TASKS = "openspec/specs/task-management/spec.md"
REPORTS = "openspec/specs/reports/spec.md"


def line_of(source: str, text: str) -> int:
    """The 1-based line a heading is written on, found the way a person would."""
    lines = source.splitlines()
    return next(index for index, line in enumerate(lines, start=1) if line.startswith(text))


def test_the_counts_are_the_ones_the_cli_reports(full_root: Path) -> None:
    # `openspec list --specs --json` over this fixture reports 2 requirements for
    # task-management and 1 for reports.
    tasks = parse_spec((full_root / TASKS).read_text(), id="task-management", file=TASKS)
    reports = parse_spec((full_root / REPORTS).read_text(), id="reports", file=REPORTS)

    assert tasks.requirement_count == 2
    assert reports.requirement_count == 1


def test_the_purpose_is_read(full_root: Path) -> None:
    spec = parse_spec((full_root / TASKS).read_text(), id="task-management", file=TASKS)

    assert spec.purpose is not None
    assert spec.purpose.startswith("Qué puede hacer alguien con sus tareas")


def test_a_requirement_keeps_its_text_and_its_scenarios(full_root: Path) -> None:
    spec = parse_spec((full_root / TASKS).read_text(), id="task-management", file=TASKS)
    requirement = spec.requirements[0]

    assert requirement.name == "Una tarea se puede dar por hecha"
    assert requirement.text.startswith("La aplicación DEBE permitir")
    assert [scenario.name for scenario in requirement.scenarios] == [
        "Marcar una tarea pendiente",
        "Desmarcar una tarea",
    ]


def test_a_scenario_keeps_its_when_and_then_as_written(full_root: Path) -> None:
    spec = parse_spec((full_root / TASKS).read_text(), id="task-management", file=TASKS)
    scenario = spec.requirements[0].scenarios[0]

    assert len(scenario.steps) == 2
    assert scenario.steps[0].startswith("**WHEN**")
    assert scenario.steps[1].startswith("**THEN**")


def test_everything_knows_which_line_it_is_on(full_root: Path) -> None:
    source = (full_root / TASKS).read_text()

    spec = parse_spec(source, id="task-management", file=TASKS)
    requirement = spec.requirements[0]

    assert requirement.location.file == TASKS
    assert requirement.location.line == line_of(source, "### Requirement: Una tarea")
    assert requirement.scenarios[0].location.line == line_of(source, "#### Scenario: Marcar")
    assert spec.requirements[1].location.line == line_of(source, "### Requirement: Las tareas")


def test_the_prose_can_be_in_any_language_because_nothing_reads_it() -> None:
    # The structural headings are English whatever the prose is, and DEBE is as good as
    # SHALL here: whether it should say SHALL is `openspec validate`'s judgement, not ours.
    spanish = (
        "## Purpose\nPara qué es esto.\n\n## Requirements\n\n"
        "### Requirement: Algo DEBE pasar\n\nY NO DEBE pasar lo otro.\n\n"
        "#### Scenario: Cuando pasa\n\n- **WHEN** ocurre\n- **THEN** se nota\n"
    )
    english = spanish.replace("DEBE", "SHALL").replace("Para qué es esto.", "What this is for.")

    from_spanish = parse_spec(spanish, id="c", file="spec.md")
    from_english = parse_spec(english, id="c", file="spec.md")

    assert from_spanish.requirement_count == from_english.requirement_count == 1
    assert len(from_spanish.requirements[0].scenarios) == 1
    assert from_spanish.requirements[0].location == from_english.requirements[0].location


def test_a_spec_with_no_purpose_says_so_rather_than_inventing_one() -> None:
    spec = parse_spec(
        "## Requirements\n\n### Requirement: Solo esto\n\nTexto.\n\n"
        "#### Scenario: Caso\n\n- **WHEN** a\n- **THEN** b\n",
        id="c",
        file="spec.md",
    )

    assert spec.purpose is None
    assert spec.requirement_count == 1


def test_an_empty_document_reads_as_an_empty_spec() -> None:
    spec = parse_spec("", id="c", file="spec.md")

    assert spec.purpose is None
    assert spec.requirements == ()
