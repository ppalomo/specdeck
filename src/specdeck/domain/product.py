"""Who this product is: its name, and the version of it that is actually running."""

from importlib.metadata import version

PRODUCT_NAME = "Specdeck"
PACKAGE_NAME = "specdeck"


def product_version() -> str:
    """Read the version from the installed package, so it cannot drift from what runs."""
    return version(PACKAGE_NAME)
