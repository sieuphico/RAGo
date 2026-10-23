"""Lệnh quản trị: `python -m app.cli add-admin <email>` (tạo quản trị viên đầu tiên)."""

import argparse
import asyncio
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.errors import AppError
from app.modules.users.service import ensure_admin


async def _add_admin(email: str) -> bool:
    engine = create_async_engine(get_settings().database_url)
    try:
        async with async_sessionmaker(engine)() as session:
            created = await ensure_admin(session, email)
            await session.commit()
            return created
    finally:
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    add_admin = sub.add_parser("add-admin", help="tạo quản trị viên đầu tiên")
    add_admin.add_argument("email")
    args = parser.parse_args(argv)
    try:
        created = asyncio.run(_add_admin(args.email))
    except AppError as exc:
        print(f"Lỗi: {exc.code.value}", file=sys.stderr)
        return 1
    print("Đã tạo quản trị viên." if created else "Quản trị viên đã tồn tại.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
