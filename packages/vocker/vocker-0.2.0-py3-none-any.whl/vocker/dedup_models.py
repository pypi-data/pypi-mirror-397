import dataclasses
import typing as ty

import sqlalchemy as sa
from sqlalchemy import orm as sao
from sqlalchemy.orm import Mapped as M, mapped_column as mc, relationship, DeclarativeBase
from sqlalchemy_boltons.orm import RelationshipComparator as Rel

from . import multihash as mh
from .util_models import now, rel_kw_basic, rel_kw_cascade


class BaseDedup(DeclarativeBase):
    pass


@BaseDedup.registry.mapped_as_dataclass(init=False)
class DedupConfig:
    __tablename__ = "dedup_config"

    key: M[str] = mc(primary_key=True)
    value: M[str] = mc(nullable=False)


@BaseDedup.registry.mapped_as_dataclass(init=False)
class DedupFile:
    """
    Represents a single deduplicated file regardless of backend (hardlink, symlink, reflink).

    The file contents may not yet be available if :attr:`pending_file` is nonempty.
    """

    __tablename__ = "dedup_file"

    id: M[int] = mc(primary_key=True)
    file_metadata: M[bytes] = mc("metadata")
    size: M[int] = mc()
    mtime: M[int] = mc()
    created_at: M[int] = mc(insert_default=now)
    orphaned_at: M[int | None] = mc()
    pending_id: M[int | None] = mc(sa.ForeignKey("dedup_pending.id", ondelete="CASCADE"))

    links: M[list["Link"]] = relationship(back_populates="file", **rel_kw_cascade)
    tags: M[list["Tag"]] = relationship(back_populates="file", **rel_kw_cascade)
    hashes: M[list["Hash"]] = relationship(back_populates="file", **rel_kw_cascade)
    pending: M["Pending | None"] = relationship(back_populates="files", **rel_kw_basic)

    # this is used as a speedup when verifying hardlinks
    _cached_file_stat = None

    @property
    def hashes_dict(self):
        return {(h := x.to_digest()).function: h for x in self.hashes}

    @classmethod
    def make_update_orphaned(cls, orphaned_at_now=None):
        """
        Construct the SQL DML statement which sets :attr:`orphaned_at` according to whether any
        links are left that point to this dedup file.
        """
        if orphaned_at_now is None:
            orphaned_at_now = now()
        L = sao.aliased(Link)
        return sa.update(cls).values(
            orphaned_at=sa.case(
                # If a Link exists, then it's NULL.
                (sa.exists().select_from(L).where(Rel(L.file) == cls), None),
                # If the orphaned_at file was set in the past, then keep that value.
                (cls.orphaned_at < orphaned_at_now, cls.orphaned_at),
                # Otherwise, set it to the current timestamp.
                else_=orphaned_at_now,
            )
        )


_make_file_fk = lambda: sa.ForeignKey("dedup_file.id", ondelete="CASCADE")


@BaseDedup.registry.mapped_as_dataclass(init=False)
class Pending:
    __tablename__ = "dedup_pending"

    id: M[int] = mc(primary_key=True)
    expire_at: M[int] = mc()

    files: M[list["DedupFile"]] = relationship(back_populates="pending", **rel_kw_cascade)


@BaseDedup.registry.mapped_as_dataclass(init=False)
class Link:
    """A link (usage) of a deduplicated file."""

    __tablename__ = "dedup_link"

    link_path: M[bytes] = mc(primary_key=True)  # utf-8 encoded
    file_id: M[int] = mc(_make_file_fk(), index=True, nullable=False)
    created_at: M[int] = mc(insert_default=now, nullable=False)

    file: M["DedupFile"] = relationship(back_populates="links", **rel_kw_basic)


tmp_bytes = sa.Table("bytes", sa.MetaData(), sa.Column("id", sa.LargeBinary, primary_key=True))
tmp_ints = sa.Table("ints", sa.MetaData(), sa.Column("id", sa.Integer, primary_key=True))
tmp_hash_lookup = sa.Table(
    "files_by_hash",
    sa.MetaData(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("hash_function", sa.Integer),
    sa.Column("digest", sa.LargeBinary),
    sa.Column("metadata_bytes", sa.LargeBinary),
)


@BaseDedup.registry.mapped_as_dataclass(init=False)
class Tag:
    __tablename__ = "dedup_tag"

    file_id: M[int] = mc(_make_file_fk(), primary_key=True, nullable=False)
    name: M[bytes] = mc(primary_key=True, index=True)

    file: M["DedupFile"] = relationship(back_populates="tags", **rel_kw_basic)


@BaseDedup.registry.mapped_as_dataclass(init=False)
class Hash:
    __tablename__ = "dedup_hashes"

    file_id: M[int] = mc(_make_file_fk(), primary_key=True, nullable=False)
    hash_function: M[int] = mc(primary_key=True)
    hash: M[bytes] = mc(index=True)

    file: M["DedupFile"] = relationship(back_populates="hashes", **rel_kw_basic)

    @classmethod
    def from_digest(cls, digest: mh.Digest, **kw):
        return cls(hash_function=digest.function.function_code, hash=digest.digest, **kw)

    def to_digest(self):
        return mh.registry.decode_from_code_and_digest(self.hash_function, self.hash)

    @classmethod
    def compare_digest(cls):
        return _HashCompareByDigest(cls)


@dataclasses.dataclass(eq=False)
class _HashCompareByDigest:
    alias: type[Hash]

    def in_(self, digests: ty.Iterable[mh.Digest]):
        a = self.alias
        return sa.tuple_(a.hash, a.hash_function).in_(
            (x.digest, x.function.function_code) for x in digests
        )

    def __eq__(self, other):
        if isinstance(other, mh.Digest):
            a = self.alias
            return sa.and_(a.hash == other.digest, a.hash_function == other.function.function_code)

        return NotImplemented

    def __ne__(self, other):
        return sa.not_(self == other)


sa.Index(
    "ix_dedup_file_pending_partial", DedupFile.pending_id, sqlite_where=DedupFile.pending_id != None
)
sa.Index(
    "ix_dedup_file_orphaned_at_partial",
    DedupFile.orphaned_at,
    sqlite_where=DedupFile.orphaned_at != None,
)
