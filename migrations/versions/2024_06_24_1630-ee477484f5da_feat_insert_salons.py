"""feat: insert salons

Revision ID: ee477484f5da
Revises: 2ac0a33fc21e
Create Date: 2024-06-24 16:30:58.346314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee477484f5da'
down_revision: Union[str, None] = '2ac0a33fc21e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """INSERT INTO salons
            VALUES
                (1, 'Лубянка', true),
                (2, 'Дача', true),
                (3, 'Империум', true),
                (4, 'Сохо', true),
                (5, 'Барби', true),
                (6, 'длятестов', true)
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.DDL("DELETE FROM salons"))
