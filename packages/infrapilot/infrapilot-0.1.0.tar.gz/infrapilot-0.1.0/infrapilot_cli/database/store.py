from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Iterable, List, Optional
from uuid import uuid4

from sqlmodel import Session, select

from infrapilot_cli.database.database import (
    CLIStateRecord,
    GitHubRepoRecord,
    InfraSnapshotRecord,
    MessageRecord,
    ThreadRecord,
    UserRecord,
    WorkspaceRecord,
    get_engine,
    utc_now,
)


@contextmanager
def _session_scope() -> Iterable[Session]:
    session = Session(get_engine(), expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _state(session: Session) -> CLIStateRecord:
    state = session.get(CLIStateRecord, 1)
    if state is None:
        state = CLIStateRecord(id=1)
        session.add(state)
        session.commit()
        session.refresh(state)
    return state


def _delete_thread_messages(session: Session, thread_id: str) -> None:
    messages = session.exec(select(MessageRecord).where(MessageRecord.thread_id == thread_id))
    for message in messages:
        session.delete(message)


def _coerce_datetime(value) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            return None
    return None


def upsert_user(user: dict) -> None:
    with _session_scope() as session:
        record = session.get(UserRecord, user["id"])
        if record is None:
            record = UserRecord(
                id=user["id"],
                auth0_sub=user.get("auth0_sub", ""),
                email=user.get("email"),
                name=user.get("name"),
                last_login=_coerce_datetime(user.get("last_login")),
            )
            session.add(record)
        else:
            record.auth0_sub = user.get("auth0_sub", record.auth0_sub)
            record.email = user.get("email", record.email)
            record.name = user.get("name", record.name)
            new_login = _coerce_datetime(user.get("last_login"))
            if new_login:
                record.last_login = new_login
            record.updated_at = utc_now()


def set_active_user(user_id: str) -> None:
    with _session_scope() as session:
        state = _state(session)
        if state.active_user_id != user_id:
            state.active_workspace_id = None
        state.active_user_id = user_id
        session.add(state)


def get_active_user_id() -> Optional[str]:
    with Session(get_engine()) as session:
        return _state(session).active_user_id


def upsert_workspace(user_id: str, workspace: dict) -> None:
    with _session_scope() as session:
        record = session.get(WorkspaceRecord, workspace["id"])
        if record is None:
            record = WorkspaceRecord(
                id=workspace["id"],
                user_id=user_id,
                name=workspace.get("name") or workspace["id"],
                region=workspace.get("region"),
                aws_profile=workspace.get("aws_profile"),
                synced_at=utc_now(),
            )
            session.add(record)
        else:
            record.name = workspace.get("name", record.name)
            record.region = workspace.get("region", record.region)
            record.aws_profile = workspace.get("aws_profile", record.aws_profile)
            record.updated_at = utc_now()
            record.synced_at = utc_now()


def list_workspaces(user_id: str) -> List[WorkspaceRecord]:
    with Session(get_engine()) as session:
        statement = (
            select(WorkspaceRecord)
            .where(WorkspaceRecord.user_id == user_id)
            .order_by(WorkspaceRecord.last_selected_at.desc(), WorkspaceRecord.created_at)
        )
        return list(session.exec(statement))


def set_active_workspace(user_id: str, workspace_id: str) -> Optional[WorkspaceRecord]:
    with _session_scope() as session:
        state = _state(session)
        state.active_workspace_id = workspace_id
        session.add(state)

        record = session.get(WorkspaceRecord, workspace_id)
        if record:
            record.last_selected_at = utc_now()
            session.add(record)
        return record


def get_active_workspace(user_id: str) -> Optional[WorkspaceRecord]:
    with Session(get_engine()) as session:
        state = _state(session)
        workspace_id = state.active_workspace_id
        if workspace_id:
            record = session.get(WorkspaceRecord, workspace_id)
            if record and record.user_id == user_id:
                return record

        statement = (
            select(WorkspaceRecord)
            .where(WorkspaceRecord.user_id == user_id)
            .order_by(WorkspaceRecord.last_selected_at.desc(), WorkspaceRecord.created_at)
        )
        return session.exec(statement).first()


# Infra snapshots ------------------------------------------------------------


def save_infra_snapshot(
    user_id: str, workspace_id: str, snapshot: dict, snapshot_hash: str | None
) -> None:
    with _session_scope() as session:
        record = session.exec(
            select(InfraSnapshotRecord).where(
                InfraSnapshotRecord.workspace_id == workspace_id,
                InfraSnapshotRecord.user_id == user_id,
            )
        ).first() or InfraSnapshotRecord(
            id=str(uuid4()),
            workspace_id=workspace_id,
            user_id=user_id,
            snapshot_json=snapshot,
            snapshot_hash=snapshot_hash,
            created_at=utc_now(),
        )
        record.snapshot_json = snapshot
        record.snapshot_hash = snapshot_hash
        record.updated_at = utc_now()
        session.add(record)


def get_infra_snapshot(workspace_id: str) -> dict | None:
    with Session(get_engine()) as session:
        record = session.exec(
            select(InfraSnapshotRecord).where(InfraSnapshotRecord.workspace_id == workspace_id)
        ).first()
        return record.snapshot_json if record else None


def get_infra_snapshot_record(workspace_id: str) -> InfraSnapshotRecord | None:
    with Session(get_engine()) as session:
        return session.exec(
            select(InfraSnapshotRecord).where(InfraSnapshotRecord.workspace_id == workspace_id)
        ).first()


# GitHub repos cache ---------------------------------------------------------


def save_github_repos(installation_id: str, account: str | None, repos: list[dict]) -> None:
    with _session_scope() as session:
        # Clear existing repos for this installation
        existing = session.exec(
            select(GitHubRepoRecord).where(GitHubRepoRecord.installation_id == installation_id)
        ).all()
        for repo in existing:
            session.delete(repo)

        now = utc_now()
        for repo in repos:
            full_name = repo.get("full_name") or repo.get("repo_full_name")
            if not full_name:
                continue
            session.add(
                GitHubRepoRecord(
                    id=str(uuid4()),
                    installation_id=installation_id,
                    full_name=full_name,
                    account=account,
                    private=repo.get("private"),
                    created_at=now,
                    updated_at=now,
                )
            )


def list_github_repos(installation_id: str | None = None) -> list[str]:
    with Session(get_engine()) as session:
        query = select(GitHubRepoRecord)
        if installation_id:
            query = query.where(GitHubRepoRecord.installation_id == installation_id)
        records = session.exec(query).all()
        return [r.full_name for r in records]


def get_workspace(workspace_id: str) -> Optional[WorkspaceRecord]:
    with Session(get_engine()) as session:
        return session.get(WorkspaceRecord, workspace_id)


def upsert_thread(workspace_id: str, thread: dict) -> None:
    with _session_scope() as session:
        workspace_record = session.get(WorkspaceRecord, workspace_id)
        user_id = workspace_record.user_id if workspace_record else None
        if not user_id:
            user_id = thread.get("user_id")
        if not user_id:
            raise ValueError("Cannot upsert thread without a user_id.")
        record = session.get(ThreadRecord, thread["id"])
        if record is None:
            record = ThreadRecord(
                id=thread["id"],
                user_id=user_id,
                workspace_id=workspace_id,
                title=thread.get("title"),
                status=thread.get("status", "open"),
                synced_at=utc_now(),
            )
            session.add(record)
        else:
            record.title = thread.get("title", record.title)
            record.status = thread.get("status", record.status)
            record.user_id = user_id or record.user_id
            record.updated_at = utc_now()
            record.synced_at = utc_now()


def list_threads(workspace_id: str) -> List[ThreadRecord]:
    with Session(get_engine()) as session:
        statement = (
            select(ThreadRecord)
            .where(ThreadRecord.workspace_id == workspace_id)
            .order_by(ThreadRecord.last_used_at.desc(), ThreadRecord.created_at.desc())
        )
        return list(session.exec(statement))


def set_active_thread(workspace_id: str, thread_id: Optional[str]) -> Optional[ThreadRecord]:
    if not thread_id:
        return None
    with _session_scope() as session:
        record = session.get(ThreadRecord, thread_id)
        if record:
            record.last_used_at = utc_now()
            session.add(record)

        workspace = session.get(WorkspaceRecord, workspace_id)
        if workspace:
            workspace.last_thread_id = thread_id
            session.add(workspace)
        return record


def delete_workspace(user_id: str, workspace_id: str) -> bool:
    with _session_scope() as session:
        workspace = session.get(WorkspaceRecord, workspace_id)
        if not workspace or workspace.user_id != user_id:
            return False

        threads = session.exec(
            select(ThreadRecord).where(ThreadRecord.workspace_id == workspace_id)
        )
        for thread in threads:
            _delete_thread_messages(session, thread.id)
            session.delete(thread)

        session.delete(workspace)

        state = _state(session)
        if state.active_workspace_id == workspace_id:
            state.active_workspace_id = None
            session.add(state)
        return True


def delete_thread(workspace_id: str, thread_id: str) -> bool:
    with _session_scope() as session:
        thread = session.get(ThreadRecord, thread_id)
        if not thread or thread.workspace_id != workspace_id:
            return False
        _delete_thread_messages(session, thread_id)
        session.delete(thread)

        workspace = session.get(WorkspaceRecord, workspace_id)
        if workspace and workspace.last_thread_id == thread_id:
            workspace.last_thread_id = None
            session.add(workspace)
        return True


def record_message(thread_id: str, message: dict) -> None:
    with _session_scope() as session:
        thread = session.get(ThreadRecord, thread_id)
        user_id = None
        if thread:
            user_id = thread.user_id
        if not user_id:
            user_id = message.get("user_id")
        if not user_id:
            raise ValueError("Cannot record message without a user_id.")
        record = MessageRecord(
            id=message.get("id") or str(uuid4()),
            thread_id=thread_id,
            user_id=user_id,
            role=message.get("role", "user"),
            content=message.get("content", ""),
            synced_at=utc_now(),
        )
        session.add(record)


def list_messages(thread_id: str, limit: Optional[int] = None) -> List[MessageRecord]:
    """Return messages for a thread in chronological order."""

    with Session(get_engine()) as session:
        statement = (
            select(MessageRecord)
            .where(MessageRecord.thread_id == thread_id)
            .order_by(MessageRecord.created_at)
        )
        if limit:
            statement = statement.limit(limit)
        return list(session.exec(statement))


__all__ = [
    "upsert_user",
    "set_active_user",
    "get_active_user_id",
    "upsert_workspace",
    "list_workspaces",
    "set_active_workspace",
    "get_active_workspace",
    "get_workspace",
    "upsert_thread",
    "list_threads",
    "set_active_thread",
    "delete_workspace",
    "delete_thread",
    "record_message",
    "list_messages",
]
