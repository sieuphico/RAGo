"""admin: allow_list_entry, audit_log, telemetry_event, job, ai_usage

Revision ID: 003
Revises: 002
"""

from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE allow_list_entry (
            email text PRIMARY KEY CHECK (email = lower(email)),
            role text NOT NULL CHECK (role IN ('BD_USER','TEAM_LEAD','ADMIN','SPONSOR')),
            added_by text NOT NULL,
            added_at timestamptz NOT NULL DEFAULT now(),
            first_login_at timestamptz NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE audit_log (
            id bigserial PRIMARY KEY,
            actor text NOT NULL,
            action text NOT NULL CHECK (action IN ('UPLOAD','DELETE','PURGE')),
            doc_id uuid NULL,
            doc_name text NULL,
            at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX ix_audit_log_at ON audit_log (at DESC)")
    # Không có cột văn bản tự do ngoài props (AD-10: chỉ siêu dữ liệu)
    op.execute(
        """
        CREATE TABLE telemetry_event (
            id bigserial PRIMARY KEY,
            event text NOT NULL,
            anon_user_id text NOT NULL,
            session_id text NOT NULL,
            ts timestamptz NOT NULL,
            app_version text NOT NULL,
            props jsonb NOT NULL DEFAULT '{}'
        )
        """
    )
    op.execute("CREATE INDEX ix_telemetry_event_ts ON telemetry_event (event, ts)")
    op.execute(
        """
        CREATE TABLE job (
            job_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            type text NOT NULL,
            payload jsonb NOT NULL,
            status text NOT NULL CHECK (status IN ('QUEUED','RUNNING','DONE','FAILED')),
            attempts int NOT NULL DEFAULT 0,
            run_after timestamptz NOT NULL DEFAULT now(),
            locked_at timestamptz NULL,
            locked_by text NULL,
            last_error text NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX ix_job_claim ON job (status, run_after)")
    op.execute(
        """
        CREATE TABLE ai_usage (
            month date PRIMARY KEY,
            cost_usd numeric(10,4) NOT NULL DEFAULT 0,
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )


def downgrade() -> None:
    for table in ("ai_usage", "job", "telemetry_event", "audit_log", "allow_list_entry"):
        op.execute(f"DROP TABLE {table}")
