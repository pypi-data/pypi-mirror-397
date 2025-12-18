from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from sqlalchemy import JSON, Column, text
from sqlmodel import Field, Session, SQLModel, create_engine

from infrapilot_cli.core.paths import resolve_cli_home

DB_PATH_ENV = "INFRAPILOT_DB_PATH"

_ENGINE = None


def _default_db_path() -> Path:
    import os

    if explicit := os.getenv(DB_PATH_ENV):
        path = Path(explicit).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    return resolve_cli_home() / "infrapilot.db"


def _ensure_engine():
    global _ENGINE
    if _ENGINE is None:
        path = _default_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        _ENGINE = create_engine(
            f"sqlite:///{path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
    return _ENGINE


def get_engine():
    return _ensure_engine()


def init_local_db() -> None:
    engine = _ensure_engine()
    SQLModel.metadata.create_all(engine)
    _run_migrations(engine)
    with Session(engine) as session:
        state = session.get(CLIStateRecord, 1)
        if state is None:
            session.add(CLIStateRecord(id=1))
            session.commit()


def get_session() -> Iterator[Session]:
    engine = _ensure_engine()
    with Session(engine) as session:
        yield session


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRecord(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    auth0_sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: Optional[datetime] = None


class WorkspaceRecord(SQLModel, table=True):
    __tablename__ = "workspaces"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(nullable=False)
    region: Optional[str] = None
    aws_profile: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: Optional[datetime] = None
    last_selected_at: Optional[datetime] = None
    last_thread_id: Optional[str] = None
    synced_at: datetime = Field(default_factory=utc_now, nullable=False)


class ThreadRecord(SQLModel, table=True):
    __tablename__ = "threads"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    workspace_id: str = Field(index=True, nullable=False)
    title: Optional[str] = None
    status: str = Field(default="open")
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    synced_at: datetime = Field(default_factory=utc_now, nullable=False)


class MessageRecord(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(primary_key=True)
    thread_id: str = Field(index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    synced_at: datetime = Field(default_factory=utc_now, nullable=False)


class CLIStateRecord(SQLModel, table=True):
    __tablename__ = "cli_state"

    id: int = Field(primary_key=True, default=1)
    active_user_id: Optional[str] = None
    active_workspace_id: Optional[str] = None


class InfraSnapshotRecord(SQLModel, table=True):
    __tablename__ = "infra_snapshots"

    id: str = Field(primary_key=True)
    workspace_id: str = Field(index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)
    snapshot_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    snapshot_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: Optional[datetime] = None


class GitHubRepoRecord(SQLModel, table=True):
    __tablename__ = "github_repos"

    id: str = Field(primary_key=True)
    installation_id: str = Field(index=True, nullable=False)
    full_name: str = Field(nullable=False)
    account: Optional[str] = None
    private: Optional[bool] = None
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: Optional[datetime] = None


def _run_migrations(engine) -> None:
    _ensure_column(engine, "workspaces", "last_selected_at", "DATETIME")
    _ensure_column(engine, "workspaces", "last_thread_id", "VARCHAR(255)")
    _ensure_column(
        engine,
        "workspaces",
        "synced_at",
        "DATETIME NOT NULL DEFAULT (datetime('now'))",
    )
    _ensure_column(engine, "threads", "last_used_at", "DATETIME")
    _ensure_column(engine, "threads", "user_id", "VARCHAR(255)")
    _ensure_column(
        engine,
        "threads",
        "synced_at",
        "DATETIME NOT NULL DEFAULT (datetime('now'))",
    )
    _ensure_column(engine, "messages", "user_id", "VARCHAR(255)")
    _ensure_column(
        engine,
        "messages",
        "synced_at",
        "DATETIME NOT NULL DEFAULT (datetime('now'))",
    )
    _ensure_table(engine, "infra_snapshots", InfraSnapshotRecord)
    _ensure_table(engine, "github_repos", GitHubRepoRecord)


def _ensure_column(engine, table: str, column: str, definition: str) -> None:
    if _column_exists(engine, table, column):
        return
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))


def _column_exists(engine, table: str, column: str) -> bool:
    query = text(f"PRAGMA table_info('{table}')")
    with engine.connect() as conn:
        result = conn.execute(query)
        return any(row[1] == column for row in result)


def _ensure_table(engine, table_name: str, model: SQLModel) -> None:
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
            {"name": table_name},
        ).fetchone()
    if exists:
        return
    model.__table__.create(bind=engine)  # type: ignore
