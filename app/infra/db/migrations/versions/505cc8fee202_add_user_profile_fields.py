"""add_user_profile_fields

Revision ID: 505cc8fee202
Revises: 7280e535f70a
Create Date: 2025-09-11 23:18:38.420225

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '505cc8fee202'
down_revision: Union[str, None] = '7280e535f70a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN first_name VARCHAR(255),
        ADD COLUMN second_name VARCHAR(255),
        ADD COLUMN birthdate DATE,
        ADD COLUMN biography TEXT,
        ADD COLUMN city VARCHAR(255)
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users 
        DROP COLUMN first_name,
        DROP COLUMN second_name,
        DROP COLUMN birthdate,
        DROP COLUMN biography,
        DROP COLUMN city
    """)
