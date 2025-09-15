"""add_search_index_for_names

Revision ID: 52604aa85467
Revises: 505cc8fee202
Create Date: 2025-09-15 00:18:21.387342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52604aa85467'
down_revision: Union[str, None] = '505cc8fee202'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем составной функциональный индекс для ускорения поиска по префиксам имен и фамилий
    op.execute("""
        CREATE INDEX idx_users_name_search ON users (
            LOWER(first_name) varchar_pattern_ops, LOWER(second_name) varchar_pattern_ops)
    """)


def downgrade() -> None:
    # Удаляем индекс при откате миграции
    op.execute("""
        DROP INDEX IF EXISTS idx_users_name_search
    """)
