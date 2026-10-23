import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import ScratchDb


def test_upgrade_downgrade(scratch_db: ScratchDb) -> None:
    scratch_db.upgrade("003")
    assert {"allow_list_entry", "audit_log", "telemetry_event", "job", "ai_usage"} <= (
        scratch_db.tables()
    )
    scratch_db.downgrade("002")
    assert "job" not in scratch_db.tables()


def test_job_claim_index(scratch_db: ScratchDb) -> None:
    scratch_db.upgrade("003")
    assert "ix_job_claim" in scratch_db.indexes()
    with scratch_db.engine.connect() as conn:
        definition = conn.execute(
            text("SELECT indexdef FROM pg_indexes WHERE indexname = 'ix_job_claim'")
        ).scalar_one()
    assert "(status, run_after)" in definition


async def test_audit_action_check(session: AsyncSession) -> None:
    with pytest.raises(IntegrityError):
        await session.execute(text("INSERT INTO audit_log (actor, action) VALUES ('a@x.vn', 'EDIT')"))


async def test_allowlist_role_check(session: AsyncSession) -> None:
    with pytest.raises(IntegrityError):
        await session.execute(
            text("INSERT INTO allow_list_entry (email, role, added_by) VALUES ('a@x.vn','GUEST','b')")
        )


async def test_telemetry_has_no_free_text_columns(session: AsyncSession) -> None:
    rows = await session.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'telemetry_event' AND data_type = 'text'"
        )
    )
    assert {r[0] for r in rows} == {"event", "anon_user_id", "session_id", "app_version"}
