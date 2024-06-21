"""feat: insert salons

Revision ID: 179c2d6fc5e2
Revises: dc24cfe94465
Create Date: 2024-06-21 18:52:57.612399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '179c2d6fc5e2'
down_revision: Union[str, None] = 'dc24cfe94465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """INSERT INTO salons
            VALUES
                (1, 'Лубянка', 1),
                (2, 'Дача', 1),
                (3, 'Империум', 1),
                (4, 'Сохо', 1),
                (5, 'Барби', 1),
                (6, 'длятестов', 1)
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.DDL("DELETE FROM salons"))
