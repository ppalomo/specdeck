"""Reading a change's `tasks.md` into the groups and tasks it is made of."""

import re

from markdown_it import MarkdownIt
from markdown_it.token import Token

from specdeck.domain.change import Task, TaskGroup, Tasks
from specdeck.domain.location import Location

CHECKBOX = re.compile(r"^\[(?P<mark>[ xX])\]\s+(?P<rest>.+)", re.DOTALL)
NUMBERED = re.compile(r"^(?P<number>\d+(?:\.\d+)*)\.?\s+(?P<text>.+)", re.DOTALL)


def parse_tasks(source: str, *, file: str) -> Tasks:
    """Read the text of a `tasks.md` into its groups and their tasks.

    Grouping follows the `## N. Title` headings. A task's line is the line its checkbox is
    written on, whatever the text does afterwards: OpenSpec's own artifacts wrap a task over
    several indented lines, and an editor opened on the second of them lands in the middle
    of a sentence.
    """
    tokens = MarkdownIt().parse(source)

    # The first section holds anything written before the first heading. It is dropped at
    # the end unless something actually landed in it.
    sections: list[tuple[str, int, list[Task]]] = [("", 1, [])]

    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2" and token.map:
            sections.append((_heading(tokens, index), token.map[0] + 1, []))
        elif token.type == "list_item_open" and token.map:
            task = _task(tokens, index, file=file, line=token.map[0] + 1)
            if task is not None:
                sections[-1][2].append(task)

    return Tasks(
        groups=tuple(
            TaskGroup(title=title, location=Location(file=file, line=line), tasks=tuple(tasks))
            for title, line, tasks in sections
            if tasks or title
        )
    )


def _heading(tokens: list[Token], index: int) -> str:
    """Read the text of the heading whose opening token is at `index`."""
    inline = tokens[index + 1] if index + 1 < len(tokens) else None
    return inline.content.strip() if inline is not None and inline.type == "inline" else ""


def _task(tokens: list[Token], index: int, *, file: str, line: int) -> Task | None:
    """Read the task a list item states, or nothing when it is not a checkbox at all."""
    written = _first_inline(tokens, index)
    if written is None:
        return None

    checkbox = CHECKBOX.match(written)
    if checkbox is None:
        return None

    # The text of a wrapped task arrives with its newlines and indentation; what is wanted
    # is the sentence it was before the line ran out.
    rest = " ".join(checkbox["rest"].split())
    numbered = NUMBERED.match(rest)
    number = numbered["number"] if numbered else ""
    text = numbered["text"] if numbered else rest

    return Task(
        number=number,
        text=text,
        done=checkbox["mark"].lower() == "x",
        location=Location(file=file, line=line),
    )


def _first_inline(tokens: list[Token], index: int) -> str | None:
    """Find the written content of a list item, up to where the item ends."""
    for token in tokens[index + 1 :]:
        if token.type == "inline":
            return token.content
        if token.type == "list_item_close":
            return None
    return None
