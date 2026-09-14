"""The layers depend inwards, and this is what says so out loud.

Layering that lives only in a document is layering that lasts until the first hurried
import. This reads the imports back out of the source, so the rule fails a build instead of
a review.
"""

import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "specdeck"

# What each layer may import from the package itself. Anything further out is out of reach:
# that is what "inwards" means, and it is the whole reason the domain can be tested without
# a disk, a port or the `openspec` binary.
ALLOWED: dict[str, frozenset[str]] = {
    "domain": frozenset({"domain"}),
    "application": frozenset({"domain", "application"}),
    "infrastructure": frozenset({"domain", "application", "infrastructure"}),
    "api": frozenset({"domain", "application", "infrastructure", "api"}),
}


def module_name(source: Path) -> str:
    """Give the dotted name a file is imported by, so relative imports resolve."""
    relative = source.relative_to(PACKAGE.parent).with_suffix("")
    parts = relative.parts[:-1] if relative.name == "__init__" else relative.parts
    return ".".join(parts)


def imported(source: Path) -> set[str]:
    """Every module of this package that a file imports, relative imports resolved."""
    package = module_name(source).rsplit(".", 1)[0]
    names: set[str] = set()

    for node in ast.walk(ast.parse(source.read_text())):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                names.add(node.module or "")
            else:
                # `from . import x` inside specdeck.domain is an import of specdeck.domain.
                anchor = package.rsplit(".", node.level - 1)[0] if node.level > 1 else package
                names.add(f"{anchor}.{node.module}" if node.module else anchor)

    return {name for name in names if name.split(".")[0] == "specdeck"}


def layer_of(module: str) -> str:
    """Which layer a module of this package belongs to. `specdeck.cli` belongs to none."""
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else ""


def sources_of(layer: str) -> list[Path]:
    return sorted((PACKAGE / layer).rglob("*.py"))


@pytest.mark.parametrize(
    "source",
    [source for layer in ALLOWED for source in sources_of(layer)],
    ids=lambda source: str(source.relative_to(PACKAGE)),
)
def test_a_layer_only_imports_inwards(source: Path) -> None:
    layer = source.relative_to(PACKAGE).parts[0]
    allowed = ALLOWED[layer]

    reached = {layer_of(module) for module in imported(source)}
    forbidden = sorted(reached - allowed)

    assert not forbidden, (
        f"{source.relative_to(PACKAGE)} is in the {layer} layer and imports "
        f"{', '.join(name or 'the package root' for name in forbidden)}. "
        f"The {layer} layer may only reach {', '.join(sorted(allowed))}."
    )


def test_every_layer_is_covered_by_the_rule() -> None:
    # A new layer added without a rule would otherwise be checked by nothing at all.
    layers = {path.name for path in PACKAGE.iterdir() if path.is_dir() and path.name.isalpha()}

    assert layers - {"static"} == set(ALLOWED)
