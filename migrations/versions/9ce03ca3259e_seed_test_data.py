"""seed_test_data

Revision ID: 9ce03ca3259e
Revises: 554da17d53b0
Create Date: 2026-07-22 17:05:38.299479

"""

from collections.abc import Sequence

import bcrypt
from alembic import op

revision: str = "9ce03ca3259e"
down_revision: str | Sequence[str] | None = "554da17d53b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    hashed_user = bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode()
    hashed_admin = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()

    op.execute(f"""
        INSERT INTO users (id, email, full_name, hashed_password, is_admin)
        VALUES (gen_random_uuid(), 'user@example.com', 'Test User', '{hashed_user}', false)
    """)  # noqa: S608

    op.execute("""
        INSERT INTO accounts (id, user_id, balance)
        SELECT gen_random_uuid(), id, 1000.00
        FROM users WHERE email = 'user@example.com'
    """)

    op.execute(f"""
        INSERT INTO users (id, email, full_name, hashed_password, is_admin)
        VALUES (gen_random_uuid(), 'admin@example.com', 'Test Admin', '{hashed_admin}', true)
    """)  # noqa: S608


def downgrade() -> None:
    op.execute("DELETE FROM payments")
    op.execute("DELETE FROM accounts")
    op.execute("DELETE FROM refresh_tokens")
    op.execute("DELETE FROM users WHERE email IN ('user@example.com', 'admin@example.com')")
