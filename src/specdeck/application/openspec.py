"""What OpenSpec's own output says, read into shapes Specdeck can use.

These models mirror the CLI's answers rather than Specdeck's domain: they are the contract
of another program, and they are kept apart so that a change over there arrives in one place
rather than everywhere. Unknown fields are ignored, so a later OpenSpec that returns more
than this knows about does not leave a root unreadable.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from specdeck.application.ports import CliOutput
from specdeck.domain.change import Artifact, ArtifactStatus
from specdeck.domain.validation import Issue, IssueLevel, Validation

NO_ROOT = "no_openspec_root"

LEVELS: dict[str, IssueLevel] = {"ERROR": "ERROR", "WARNING": "WARNING", "INFO": "INFO"}
UNKNOWN_LEVEL: IssueLevel = "WARNING"
"""Where a level Specdeck has never seen lands. Shown rather than hidden, and never turned
into an error: whether an item is valid is the CLI's to say, not ours to infer from a word."""

STATUSES: dict[str, ArtifactStatus] = {
    "done": "done",
    "ready": "ready",
    "blocked": "blocked",
    "skipped": "skipped",
}


class CliModel(BaseModel):
    """Something the OpenSpec CLI said, in the shape it said it."""

    model_config = ConfigDict(frozen=True, extra="ignore", populate_by_name=True)


class UnreadableAnswerError(Exception):
    """The CLI answered with something that was not the JSON it promises."""

    def __init__(self, exit_code: int, stderr: str) -> None:
        """Say what came back instead."""
        said = stderr.strip().splitlines()
        message = (
            f"the OpenSpec CLI answered with no JSON document (exit {exit_code})"
            f"{': ' + said[0] if said else ''}"
        )
        super().__init__(message)


class RootProblem(CliModel):
    """Something the CLI has to say about the path it was pointed at."""

    severity: str = ""
    code: str = ""
    message: str = ""


class ChangeSummary(CliModel):
    """One active change, as `openspec list --json` reports it."""

    name: str
    completed_tasks: int = Field(default=0, alias="completedTasks")
    total_tasks: int = Field(default=0, alias="totalTasks")
    last_modified: datetime | None = Field(default=None, alias="lastModified")
    status: str = ""


class ChangeList(CliModel):
    """The answer to `openspec list --json`. Active changes only; never the archive."""

    changes: tuple[ChangeSummary, ...] = ()
    status: tuple[RootProblem, ...] = ()


class SpecSummary(CliModel):
    """One capability, as `openspec list --specs --json` reports it."""

    id: str
    requirement_count: int = Field(default=0, alias="requirementCount")


class SpecList(CliModel):
    """The answer to `openspec list --specs --json`."""

    specs: tuple[SpecSummary, ...] = ()
    status: tuple[RootProblem, ...] = ()


class ArtifactReport(CliModel):
    """One node of a change's pipeline, as the CLI reports it."""

    id: str
    status: str = ""
    requires: tuple[str, ...] = ()
    output_path: str = Field(default="", alias="outputPath")


class ChangeStatus(CliModel):
    """One change's pipeline, as `openspec status --all --json` reports it."""

    change_name: str = Field(alias="changeName")
    schema_name: str | None = Field(default=None, alias="schemaName")
    is_complete: bool = Field(default=False, alias="isComplete")
    artifacts: tuple[ArtifactReport, ...] = ()


class StatusReport(CliModel):
    """The answer to `openspec status --all --json`."""

    changes: tuple[ChangeStatus, ...] = ()
    status: tuple[RootProblem, ...] = ()


class IssueReport(CliModel):
    """One thing the CLI has to say about one artifact."""

    level: str = ""
    path: str = ""
    message: str = ""


class ValidationItem(CliModel):
    """The verdict on one change or one spec."""

    id: str
    type: str = ""
    valid: bool = False
    issues: tuple[IssueReport, ...] = ()


class ValidationReport(CliModel):
    """The answer to `openspec validate --all --json`, whatever the exit code was."""

    items: tuple[ValidationItem, ...] = ()
    status: tuple[RootProblem, ...] = ()


def read[Answer: CliModel](output: CliOutput, into: type[Answer]) -> Answer:
    """Read what the CLI answered, paying no attention to how it exited.

    `validate` exits non-zero the moment any item is invalid and writes its whole report
    anyway, and a path that is not a root explains itself in JSON while exiting non-zero too.
    The document is the answer; the exit code is a hint about it.
    """
    if output.document is None:
        raise UnreadableAnswerError(output.exit_code, output.stderr)

    return into.model_validate(output.document)


def not_a_root(answer: ChangeList | SpecList | StatusReport | ValidationReport) -> str | None:
    """Give the CLI's own words for why a path is not a root, when that is what it said."""
    problem = next((one for one in answer.status if one.code == NO_ROOT), None)
    return problem.message if problem is not None else None


def as_validation(item: ValidationItem) -> Validation:
    """Turn one item's verdict into what the domain holds, levels kept apart."""
    return Validation(
        valid=item.valid,
        issues=tuple(
            Issue(
                level=LEVELS.get(issue.level.upper(), UNKNOWN_LEVEL),
                path=issue.path,
                message=issue.message,
            )
            for issue in item.issues
        ),
    )


def as_artifact(report: ArtifactReport) -> Artifact:
    """Turn one reported pipeline node into what the domain holds."""
    return Artifact(
        id=report.id,
        status=STATUSES.get(report.status, "blocked"),
        files=(report.output_path,) if report.output_path else (),
        requires=report.requires,
    )
