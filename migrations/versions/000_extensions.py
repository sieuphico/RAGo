"""extensions: vector, unaccent, cwd_unaccent

Revision ID: 000
Revises:
"""

from alembic import op

revision = "000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    # unaccent() không IMMUTABLE nên không dùng được trong cột sinh/chỉ mục
    op.execute(
        "CREATE FUNCTION cwd_unaccent(text) RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE "
        "AS $$ SELECT public.unaccent('public.unaccent', $1) $$"
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS cwd_unaccent(text)")
    op.execute("DROP EXTENSION IF EXISTS unaccent")
    op.execute("DROP EXTENSION IF EXISTS vector")
