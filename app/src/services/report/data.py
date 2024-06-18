from dataclasses import dataclass

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.services.db.dao.salon_dao import SalonDao
from app.src.services.report.enums import AnswerType
from app.src.services.sheets.sheet import get_data_from_sheet


class Answer(BaseModel):
    """Ответ на каждый вопрос."""

    number: int
    data: str
    type: AnswerType
    question: str


@dataclass(slots=True, frozen=True)
class Question:
    """Данные вопроса."""

    id: int
    text: str
    description: str
    type: AnswerType
    require: bool


async def get_questions() -> dict[int, Question]:
    questions = {}
    sheet_data = await get_data_from_sheet()
    for index, row in enumerate(sheet_data, start=1):
        question = Question(
            id=index,
            text=row[0],
            description=row[2],
            type=AnswerType.Photo if row[4] else AnswerType.Text,
            require=bool(row[1])
        )
        questions[index] = question
    return questions


async def get_salons(db: AsyncSession) -> dict[str, int]:
    salons = await SalonDao(db).find_all()
    return {salon.name: salon.id for salon in salons}


QUESTIONS = {
    1: Question(
        id=1,
        text="Чек лист обхода (перед сменой)",
        description="Пришли фото листа",
        type=AnswerType.Photo,
        require=True,
    ),
    2: Question(
        id=2,
        text="Номера дев",
        description="Пришли фото заполненной таблицы",
        type=AnswerType.Photo,
        require=True,
    ),
    3: Question(
        id=3,
        text="Номера муж",
        description="Пришли фото заполненной таблицы",
        type=AnswerType.Photo,
        require=True,
    ),
    4: Question(
        id=4,
        text="Включённый телевизор с порно в рабочей комнате(Барби,Сохо)",
        description='Пришли фото с Барби и Сохо с других салонов напиши "нет"',
        type=AnswerType.Text,
        require=True,
    ),
    5: Question(
        id=5,
        text="Невыход,опоздания,проставленные штрафы (сумки,туфли)",
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    6: Question(
        id=6,
        text="Статусы в вотсап минимум 5шт",
        description="Пришли фото",
        type=AnswerType.Photo,
        require=True,
    ),
    7: Question(
        id=7,
        text="Чек-лист проверки дев",
        description="Пришли фото",
        type=AnswerType.Photo,
        require=True,
    ),
    8: Question(
        id=8,
        text="Кто оставил больше 40к",
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    9: Question(
        id=9,
        text="Высокие ЗП(не меньше 6 зп)",
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    10: Question(
        id=10,
        text="Отчет по брифингу",
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    11: Question(
        id=11,
        text="Отчет после смены",
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    12: Question(
        id=12,
        text="Отчет по загару ",
        description="Напиши текстом кто не загорелый ",
        type=AnswerType.Text,
        require=True,
    ),
    13: Question(
        id=13,
        text="Фото поставленных на зарядку планшетов и колонок",
        description="Пришли фотоотчет ",
        type=AnswerType.Photo,
        require=True,
    ),
    14: Question(
        id=14,
        text="Отправить отзывы (скрин переписки с Кристиной)",
        description="Пришли фото",
        type=AnswerType.Photo,
        require=True,
    ),
    15: Question(
        id=15,
        text="Закрыть CRM",
        description="Пришли фото пустой CRM",
        type=AnswerType.Photo,
        require=True,
    ),
    16: Question(
        id=16,
        text="Фото включенных ТВ в гостевых",
        description="Пришли фото",
        type=AnswerType.Photo,
        require=True,
    ),
    17: Question(
        id=17,
        text="Фото включенных тв у девочек",
        description="Пришли фото",
        type=AnswerType.Photo,
        require=True,
    ),
    18: Question(
        id=18,
        text="Отчет по продажам(план продаж Регине)",
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    19: Question(
        id=19,
        text="Количество проданных сертификатов( имя номер гостя ТОЛЬКО ВАШИ ПРОДАЖИ)",
        description="напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    20: Question(
        id=20,
        text="Кому был сделан перерасчет за допы",
        description="Напиши текстом имена девочек",
        type=AnswerType.Text,
        require=True,
    ),
    21: Question(
        id=21,
        text=(
            "Напиши кто по твоим наблюдениям негативил из персонала, кто вызывает у "
            "тебя подозрения"
        ),
        description="Напиши текстом имена девочек",
        type=AnswerType.Text,
        require=True,
    ),
    22: Question(
        id=22,
        text=(
            "Сколько гостей от таксистов было в течении смены? Сколько всего было "
            "гостей за смену ? Были иностранцы? В каких отелях остановились?"
        ),
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    23: Question(
        id=23,
        text=(
            "Мастера,которые не заработали,напиши текстом кто у тебя на "
            "смене не зарабоатл и что ты для этого сделала, предложила пойти накласс "
            "массаж в 4 руки или может девушку с 50% скидкой?"
        ),
        description="Напиши текстом",
        type=AnswerType.Text,
        require=True,
    ),
    24: Question(
        id=24,
        text="Фото ежедневника (задачи на день)",
        description="Пришли фото",
        type=AnswerType.Photo,
        require=True,
    ),
    25: Question(
        id=25,
        text="Чек лист обхода(после смены)",
        description="Пришли фото",
        type=AnswerType.Photo,
        require=True,
    ),
}
