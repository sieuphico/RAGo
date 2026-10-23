import asyncio
import inspect
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.domain import Role
from app.modules.audit import repository as audit
from app.modules.telemetry.repository import TelemetryRow, append_event, events_between
from app.modules.usage import repository as usage
from app.modules.users import repository as users

T0 = datetime(2026, 11, 2, 8, tzinfo=UTC)


async def test_email_case_insensitive(session: AsyncSession) -> None:
    await users.add(session, "Lan@CongTy.vn", Role.BD_USER, "admin@congty.vn")
    found = await users.get_by_email(session, "lan@congty.vn")
    assert found is not None and found.email == "lan@congty.vn"
    assert await users.get_by_email(session, "Lan@CongTy.vn") is not None


async def test_users_counts_and_mark_login(session: AsyncSession) -> None:
    await users.add(session, "a@x.vn", Role.ADMIN, "root")
    await users.add(session, "b@x.vn", Role.BD_USER, "root")
    assert await users.count(session) == 2
    assert await users.count_by_role(session, Role.ADMIN) == 1
    assert await users.mark_login(session, "A@x.vn", T0) is True
    assert await users.mark_login(session, "a@x.vn", T0) is False
    assert await users.remove(session, "b@x.vn") is True
    assert await users.remove(session, "b@x.vn") is False


def test_audit_append_only() -> None:
    public = {
        name
        for name, fn in inspect.getmembers(audit, inspect.iscoroutinefunction)
        if fn.__module__ == audit.__name__ and not name.startswith("_")
    }
    assert public == {"append", "list_since", "delete_before"}


async def test_audit_list_order(session: AsyncSession) -> None:
    for i in range(3):
        await audit.append(session, f"u{i}@x.vn", "UPLOAD", None, f"{i}.pdf")
        await session.execute(
            text("UPDATE audit_log SET at = :t WHERE actor = :a"),
            {"t": T0 + timedelta(minutes=i), "a": f"u{i}@x.vn"},
        )
    rows = await audit.list_since(session, T0, 100)
    assert [r.actor for r in rows] == ["u2@x.vn", "u1@x.vn", "u0@x.vn"]
    assert await audit.delete_before(session, T0 + timedelta(minutes=1)) == 1


async def test_telemetry_roundtrip(session: AsyncSession) -> None:
    await append_event(
        session, TelemetryRow("question_submitted", "anon", "s1", T0, "0.0.0", {"length_chars": 5})
    )
    rows = await events_between(session, ["question_submitted"], T0, T0 + timedelta(hours=1))
    assert [r.props for r in rows] == [{"length_chars": 5}]
    assert await events_between(session, ["other"], T0, T0 + timedelta(hours=1)) == []


async def test_usage_add_cost_concurrent(test_database_url: str) -> None:
    month = date(2026, 11, 1)
    engine = create_async_engine(test_database_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def add() -> None:
        async with factory() as s:
            await usage.add_cost(s, month, 1.5)
            await s.commit()

    try:
        await asyncio.gather(add(), add())
        async with factory() as s:
            assert await usage.get_cost(s, month) == 3.0
            await s.execute(text("DELETE FROM ai_usage"))
            await s.commit()
    finally:
        await engine.dispose()
