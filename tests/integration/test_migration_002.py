import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import ScratchDb


def test_upgrade_downgrade(scratch_db: ScratchDb) -> None:
    scratch_db.upgrade("002")
    assert {"chat_session", "message", "citation", "rating"} <= scratch_db.tables()
    scratch_db.downgrade("001")
    assert "message" not in scratch_db.tables()


async def _session_and_message(
    session: AsyncSession, role: str = "assistant"
) -> tuple[uuid.UUID, uuid.UUID]:
    sid, mid = uuid.uuid4(), uuid.uuid4()
    await session.execute(
        text("INSERT INTO chat_session (session_id, user_email) VALUES (:s, 'u@x.vn')"), {"s": sid}
    )
    await session.execute(
        text(
            "INSERT INTO message (message_id, session_id, role, status) "
            "VALUES (:m, :s, :r, 'COMPLETED')"
        ),
        {"m": mid, "s": sid, "r": role},
    )
    return sid, mid


async def _doc(session: AsyncSession) -> uuid.UUID:
    doc_id = uuid.uuid4()
    await session.execute(
        text(
            "INSERT INTO document (doc_id, name, uploaded_by, size_bytes, status, file_key) "
            "VALUES (:id, 'a.pdf', 'u@x.vn', 10, 'READY', :k)"
        ),
        {"id": doc_id, "k": f"k-{doc_id}"},
    )
    return doc_id


async def _citation(session: AsyncSession, mid: uuid.UUID, doc_id: uuid.UUID, snippet: str) -> None:
    await session.execute(
        text("INSERT INTO citation VALUES (:m, 1, :d, 3, :s)"),
        {"m": mid, "d": doc_id, "s": snippet},
    )


async def test_snippet_length_check(session: AsyncSession) -> None:
    _, mid = await _session_and_message(session)
    doc_id = await _doc(session)
    await _citation(session, mid, doc_id, "x" * 200)
    with pytest.raises(IntegrityError):
        await _citation(session, mid, doc_id, "x" * 201)


async def test_session_cascade(session: AsyncSession) -> None:
    sid, mid = await _session_and_message(session)
    await session.execute(
        text("INSERT INTO message (session_id, role, status) VALUES (:s, 'user', 'COMPLETED')"),
        {"s": sid},
    )
    await _citation(session, mid, await _doc(session), "s")
    await session.execute(text("INSERT INTO rating (message_id, value) VALUES (:m, 'UP')"), {"m": mid})
    await session.execute(text("DELETE FROM chat_session WHERE session_id = :s"), {"s": sid})
    for table in ("message", "citation", "rating"):
        count = (await session.execute(text(f"SELECT count(*) FROM {table}"))).scalar_one()
        assert count == 0, table


async def test_role_check(session: AsyncSession) -> None:
    with pytest.raises(IntegrityError):
        await _session_and_message(session, role="system")
