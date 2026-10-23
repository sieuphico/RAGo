"""documents: document, chunk, suggestion

Revision ID: 001
Revises: 000

Số chiều vector lấy từ cấu hình `embedding_dim` lúc chạy migration. Đổi mô hình
nhúng thì phải tạo lại cột `chunk.embedding` và lập chỉ mục lại.
"""

from alembic import op

from app.core.config import get_settings

revision = "001"
down_revision = "000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dim = get_settings().embedding_dim
    op.execute(
        """
        CREATE TABLE document (
            doc_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL CHECK (char_length(name) <= 255),
            uploaded_by text NOT NULL,
            uploaded_at timestamptz NOT NULL DEFAULT now(),
            size_bytes bigint NOT NULL,
            page_count int NULL,
            status text NOT NULL CHECK (
                status IN ('PROCESSING','OCR_PROCESSING','READY','FAILED','DELETED')),
            failure_reason text NULL CHECK (
                failure_reason IN ('FILE_CORRUPTED','FILE_ENCRYPTED','OCR_UNREADABLE',
                                   'PROCESSING_ERROR')),
            used_ocr boolean NOT NULL DEFAULT false,
            file_key text NOT NULL UNIQUE,
            processed_at timestamptz NULL,
            deleted_at timestamptz NULL
        )
        """
    )
    op.execute(
        f"""
        CREATE TABLE chunk (
            chunk_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            doc_id uuid NOT NULL REFERENCES document(doc_id) ON DELETE CASCADE,
            page int NOT NULL CHECK (page >= 1),
            text text NOT NULL,
            embedding vector({dim}) NOT NULL,
            tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', cwd_unaccent(text))) STORED,
            lang text NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE suggestion (
            doc_id uuid PRIMARY KEY REFERENCES document(doc_id) ON DELETE CASCADE,
            questions jsonb NOT NULL CHECK (
                jsonb_typeof(questions) = 'array' AND jsonb_array_length(questions) = 3),
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_chunk_embedding_hnsw ON chunk USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute("CREATE INDEX ix_chunk_tsv_gin ON chunk USING gin (tsv)")
    op.execute("CREATE INDEX ix_chunk_doc_page ON chunk (doc_id, page)")
    op.execute("CREATE INDEX ix_document_status_uploaded ON document (status, uploaded_at DESC)")


def downgrade() -> None:
    op.execute("DROP TABLE suggestion")
    op.execute("DROP TABLE chunk")
    op.execute("DROP TABLE document")
