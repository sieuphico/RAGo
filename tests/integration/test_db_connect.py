from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_db_connects(session: AsyncSession) -> None:
    assert (await session.execute(text("SELECT 1"))).scalar_one() == 1


async def test_extensions_installed(session: AsyncSession) -> None:
    rows = await session.execute(text("SELECT extname FROM pg_extension"))
    assert {"vector", "unaccent"} <= {r[0] for r in rows}


async def test_cwd_unaccent(session: AsyncSession) -> None:
    result = await session.execute(text("SELECT cwd_unaccent('Hợp đồng Đà Nẵng')"))
    assert result.scalar_one() == "Hop dong Da Nang"


async def test_rollback_between_tests_part1(session: AsyncSession) -> None:
    await session.execute(text("CREATE TABLE IF NOT EXISTS rb_probe (id int)"))
    await session.execute(text("INSERT INTO rb_probe VALUES (1)"))
    count = (await session.execute(text("SELECT count(*) FROM rb_probe"))).scalar_one()
    assert count == 1


async def test_rollback_between_tests_part2(session: AsyncSession) -> None:
    # bảng và dòng của test trước đã rollback cùng giao dịch
    exists = (await session.execute(text("SELECT to_regclass('rb_probe')"))).scalar_one()
    assert exists is None
