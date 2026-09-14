"""The common shape of everything the domain holds."""

from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """A fact derived from disk.

    Frozen, because nothing in the domain is edited in place: the files are the truth and
    everything here is a cache of them, replaced whole when they change.

    `extra='ignore'` is Pydantic's default, said out loud because a decision rests on it:
    the models that carry OpenSpec's own output must survive a version of it that returns
    fields Specdeck has never heard of.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")
