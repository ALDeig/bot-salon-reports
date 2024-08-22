from app.src.services.db.dao.holder import HolderDao


async def save_user(
    dao: HolderDao, user_id: int, full_name: str, username: str | None
):
    await dao.user_dao.insert_or_nothing(
        index_element="id", id=user_id, full_name=full_name, username=username
    )
