"""feat: insert salons

Revision ID: c63ae70dcb38
Revises: 8273604bcbab
Create Date: 2024-06-18 16:26:14.296923

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c63ae70dcb38"
down_revision: Union[str, None] = "8273604bcbab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """INSERT INTO salons
            VALUES
                (1, 'Лубянка'),
                (2, 'Дача'),
                (3, 'Империум'),
                (4, 'Сохо'),
                (5, 'Барби'),
                (6, 'длятестов')
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.DDL("DELETE FROM salons"))
