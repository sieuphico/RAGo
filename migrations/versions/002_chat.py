"""chat: chat_session, message, citation, rating

Revision ID: 002
Revises: 001
"""

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE chat_session (
            session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_email text NOT NULL,
            title text NULL CHECK (char_length(title) <= 60),
            created_at timestamptz NOT NULL DEFAULT now(),
            last_message_at timestamptz NOT NULL DEFAULT now(),
            scope_doc_ids uuid[] NOT NULL DEFAULT '{}'
        )
        """
    )
    op.execute(
        """
        CREATE TABLE message (
            message_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id uuid NOT NULL REFERENCES chat_session(session_id) ON DELETE CASCADE,
            role text NOT NULL CHECK (role IN ('user','assistant')),
            text text NOT NULL DEFAULT '',
            status text NOT NULL CHECK (
                status IN ('SEARCHING','STREAMING','COMPLETED','NOT_FOUND','STOPPED',
                           'INTERRUPTED','FAILED')),
            is_not_found boolean NOT NULL DEFAULT false,
            latency_ms int NULL,
            error_code text NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    # Không cascade theo document: tài liệu đã xóa vẫn giữ hàng trích dẫn (EC-14)
    op.execute(
        """
        CREATE TABLE citation (
            message_id uuid NOT NULL REFERENCES message(message_id) ON DELETE CASCADE,
            idx int NOT NULL,
            doc_id uuid NOT NULL REFERENCES document(doc_id),
            page int NOT NULL,
            snippet text NOT NULL CHECK (char_length(snippet) <= 200),
            PRIMARY KEY (message_id, idx)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE rating (
            message_id uuid PRIMARY KEY REFERENCES message(message_id) ON DELETE CASCADE,
            value text NOT NULL CHECK (value IN ('UP','DOWN')),
            reason_code text NULL CHECK (
                reason_code IN ('WRONG_INFO','WRONG_CITATION','MISSING_INFO','OTHER')),
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX ix_session_user_last ON chat_session (user_email, last_message_at DESC)")
    op.execute("CREATE INDEX ix_message_session_created ON message (session_id, created_at)")


def downgrade() -> None:
    op.execute("DROP TABLE rating")
    op.execute("DROP TABLE citation")
    op.execute("DROP TABLE message")
    op.execute("DROP TABLE chat_session")
