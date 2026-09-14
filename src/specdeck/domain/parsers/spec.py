"""Reading a `spec.md` into the requirements and scenarios it states.

The same document shape serves twice: the current spec of a capability, and the delta a
change proposes over it. What tells them apart is the `## …` section each requirement was
written under, so both are read by the same pass and separated afterwards.
"""

import re

from markdown_it import MarkdownIt
from markdown_it.token import Token

from specdeck.domain.location import Location
from specdeck.domain.spec import Delta, Operation, Requirement, Scenario, Spec

OPERATIONS: dict[str, Operation] = {
    "ADDED": "ADDED",
    "MODIFIED": "MODIFIED",
    "REMOVED": "REMOVED",
    "RENAMED": "RENAMED",
}

REQUIREMENT = re.compile(r"^Requirement:\s*(?P<name>.+)$", re.DOTALL)
SCENARIO = re.compile(r"^Scenario:\s*(?P<name>.+)$", re.DOTALL)
PURPOSE = "Purpose"
LISTS = {"bullet_list_open", "ordered_list_open", "bullet_list_close", "ordered_list_close"}

# A requirement paired with the `## …` section it was written under. The current spec has
# one section called Requirements; a delta has one per operation it declares.
Section = tuple[str, Requirement]


def parse_spec(source: str, *, id: str, file: str) -> Spec:  # noqa: A002
    """Read the text of a current spec into the capability it describes.

    Nothing here looks at the language of the prose. OpenSpec's structural headings are
    English even when everything under them is not, and whether a requirement says SHALL or
    DEBE is for `openspec validate` to judge, not for the reader of the file.
    """
    reader = _read(source, file=file)

    return Spec(
        id=id,
        purpose=reader.purpose(),
        requirements=tuple(requirement for _, requirement in reader.sections),
    )


def parse_deltas(source: str, *, capability: str, file: str) -> tuple[Delta, ...]:
    """Read a change's delta spec into what it proposes to do to one capability.

    A delta is never the whole spec: it states only the edit, which is why it carries the
    operation and the current spec does not. A RENAMED section states its edit in FROM and
    TO lines rather than in requirements, so it is reported by having been there at all.
    """
    reader = _read(source, file=file)

    proposed: dict[Operation, list[Requirement]] = {
        operation: []
        for heading in reader.headings
        if (operation := _operation(heading)) is not None
    }

    for heading, requirement in reader.sections:
        operation = _operation(heading)
        if operation is not None:
            proposed[operation].append(requirement)

    return tuple(
        Delta(capability=capability, operation=operation, requirements=tuple(requirements))
        for operation, requirements in proposed.items()
    )


class _Reader:
    """A spec taking shape as its headings and paragraphs go past.

    Markdown gives no nesting to lean on here: a requirement is everything written after its
    heading until the next one of the same rank or higher. So the reader keeps what is open
    and closes it when the next heading says it has ended.
    """

    def __init__(self, file: str) -> None:
        self.file = file
        self.sections: list[Section] = []
        self.headings: list[str] = []
        self._purpose: list[str] = []
        self._section = ""
        self._name = ""
        self._line = 1
        self._text: list[str] = []
        self._scenarios: list[Scenario] = []
        self._open: tuple[str, int] | None = None
        self._steps: list[str] = []

    def purpose(self) -> str | None:
        """Give what the capability is for, or nothing when it never said."""
        return "\n\n".join(self._purpose).strip() or None

    def section(self, heading: str) -> None:
        """Start a `## …` section. Whatever was open belonged to the previous one."""
        self._close_requirement()
        self._section = heading
        self.headings.append(heading)

    def requirement(self, name: str, line: int) -> None:
        """Start a requirement."""
        self._close_requirement()
        self._name, self._line = name, line

    def scenario(self, name: str, line: int) -> None:
        """Start a scenario under the requirement that is open."""
        self._close_scenario()
        self._open, self._steps = (name, line), []

    def wrote(self, content: str, *, in_list: bool) -> None:
        """Put a piece of written content wherever the reader currently is."""
        if self._open is not None:
            # A scenario is its WHEN/THEN lines; prose written beside them is not a step.
            if in_list:
                self._steps.append(content)
        elif self._name:
            self._text.append(content)
        elif self._section == PURPOSE:
            self._purpose.append(content)

    def finish(self) -> None:
        """Close whatever the end of the document left open."""
        self._close_requirement()

    def _close_scenario(self) -> None:
        if self._open is None:
            return
        name, line = self._open
        self._scenarios.append(
            Scenario(
                name=name,
                location=Location(file=self.file, line=line),
                steps=tuple(self._steps),
            )
        )
        self._open = None

    def _close_requirement(self) -> None:
        self._close_scenario()
        if self._name:
            self.sections.append(
                (
                    self._section,
                    Requirement(
                        name=self._name,
                        text="\n\n".join(self._text).strip(),
                        location=Location(file=self.file, line=self._line),
                        scenarios=tuple(self._scenarios),
                    ),
                )
            )
        self._name, self._text, self._scenarios = "", [], []


def _read(source: str, *, file: str) -> _Reader:
    """Walk the document once, handing every heading and paragraph to a reader."""
    tokens = MarkdownIt().parse(source)
    reader = _Reader(file)
    depth = 0
    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token.type == "heading_open":
            _open(reader, tokens, index)
            index += 3  # heading_open, its inline, heading_close
            continue

        if token.type in LISTS:
            depth += 1 if token.type.endswith("_open") else -1
        elif token.type == "inline":
            reader.wrote(token.content.strip(), in_list=depth > 0)

        index += 1

    reader.finish()
    return reader


def _open(reader: _Reader, tokens: list[Token], index: int) -> None:
    """Tell the reader which heading has just started."""
    token = tokens[index]
    heading = _heading(tokens, index)
    line = token.map[0] + 1 if token.map else 1

    if token.tag == "h2":
        reader.section(heading)
    elif (requirement := REQUIREMENT.match(heading)) is not None:
        reader.requirement(requirement["name"].strip(), line)
    elif (scenario := SCENARIO.match(heading)) is not None:
        reader.scenario(scenario["name"].strip(), line)


def _heading(tokens: list[Token], index: int) -> str:
    """Read the text of the heading whose opening token is at `index`."""
    inline = tokens[index + 1] if index + 1 < len(tokens) else None
    return inline.content.strip() if inline is not None and inline.type == "inline" else ""


def _operation(heading: str) -> Operation | None:
    """Recognise the operation a `## ADDED Requirements` heading declares, if any."""
    word, _, rest = heading.partition(" ")
    return OPERATIONS.get(word) if rest.strip() == "Requirements" else None
