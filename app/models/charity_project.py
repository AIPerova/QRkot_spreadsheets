from sqlalchemy import Column, String, Text

from app.core.constants import MAX_NAME_LENGTH
from app.models.base import CharityBase


class CharityProject(CharityBase):
    """Модель для проекта пожертвований."""
    name = Column(
        String(MAX_NAME_LENGTH), unique=True, nullable=False,
    )
    description = Column(Text, nullable=False)

    def __repr__(self):
        remains = self.full_amount - self.invested_amount
        return (
            f'Для проекта {self.name} осталось собрать {remains} руб.'
        )