import datetime
from datetime import timezone


def now() -> int:
    return int(datetime.datetime.now(timezone.utc).timestamp())


rel_kw_basic = dict(repr=False, lazy="raise")

# Coupled with ForeignKey(..., ondelete="CASCADE"), this implements automatic deletion of child
# records when the parent is deleted.
rel_kw_cascade = rel_kw_basic | dict(cascade="all, delete", passive_deletes=True)
