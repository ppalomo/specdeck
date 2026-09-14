"""Reading `tasks.md`: the groups, the tasks, and the line each checkbox is written on."""

from pathlib import Path

from specdeck.domain.parsers.tasks import parse_tasks

FILE = "openspec/changes/add-reminders/tasks.md"


def line_of(source: str, prefix: str) -> int:
    """The 1-based line the given checkbox is written on, found the way a person would."""
    lines = source.splitlines()
    return next(index for index, line in enumerate(lines, start=1) if line.startswith(prefix))


def test_the_groups_are_the_headings(full_root: Path) -> None:
    source = (full_root / FILE).read_text()

    tasks = parse_tasks(source, file=FILE)

    assert [group.title for group in tasks.groups] == ["1. El modelo", "2. La interfaz"]
    assert tasks.groups[0].location.line == line_of(source, "## 1. El modelo")
    assert tasks.groups[0].location.file == FILE


def test_the_counts_are_the_ones_the_cli_reports(full_root: Path) -> None:
    # `openspec list --json` over this fixture reports 4 tasks, 1 of them complete, for
    # add-reminders. Our own parse has to agree with it or one of the two is lying.
    tasks = parse_tasks((full_root / FILE).read_text(), file=FILE)

    assert tasks.total == 4
    assert tasks.done == 1


def test_the_other_change_agrees_with_the_cli_too(full_root: Path) -> None:
    file = "openspec/changes/retire-old-reports/tasks.md"

    tasks = parse_tasks((full_root / file).read_text(), file=file)

    assert (tasks.total, tasks.done) == (3, 2)


def test_a_task_that_wraps_is_one_task_with_its_sentence_whole(full_root: Path) -> None:
    source = (full_root / FILE).read_text()

    tasks = parse_tasks(source, file=FILE)
    wrapped = tasks.groups[0].tasks[1]

    assert wrapped.number == "1.2"
    assert not wrapped.done
    # The text is the sentence, not the lines it happened to be broken over.
    assert "\n" not in wrapped.text
    assert wrapped.text.startswith("Escribir el envío del aviso")
    assert wrapped.text.endswith("en varias líneas indentadas como esta.")


def test_the_line_is_the_checkbox_and_not_where_the_text_ends(full_root: Path) -> None:
    source = (full_root / FILE).read_text()

    tasks = parse_tasks(source, file=FILE)
    wrapped = tasks.groups[0].tasks[1]

    assert wrapped.location.line == line_of(source, "- [ ] 1.2")
    assert source.splitlines()[wrapped.location.line - 1].startswith("- [ ] 1.2")


def test_what_is_done_is_read_from_the_mark() -> None:
    source = "## 1. G\n\n- [x] 1.1 Hecha.\n- [X] 1.2 Hecha también.\n- [ ] 1.3 Pendiente.\n"

    tasks = parse_tasks(source, file="tasks.md")

    assert [task.done for task in tasks.groups[0].tasks] == [True, True, False]


def test_a_bullet_that_is_not_a_checkbox_is_not_a_task() -> None:
    source = "## 1. G\n\n- Una nota suelta, que no es una tarea.\n- [ ] 1.1 Esta sí.\n"

    tasks = parse_tasks(source, file="tasks.md")

    assert tasks.total == 1
    assert tasks.groups[0].tasks[0].number == "1.1"


def test_a_task_without_a_number_keeps_its_whole_text() -> None:
    source = "## 1. G\n\n- [ ] Sin número, pero es una tarea.\n"

    tasks = parse_tasks(source, file="tasks.md")
    task = tasks.groups[0].tasks[0]

    assert task.number == ""
    assert task.text == "Sin número, pero es una tarea."


def test_a_file_with_no_tasks_reads_as_no_tasks() -> None:
    assert parse_tasks("", file="tasks.md").total == 0
    assert parse_tasks("Sólo prosa, ninguna casilla.\n", file="tasks.md").groups == ()
