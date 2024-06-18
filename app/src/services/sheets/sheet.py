from gspread.utils import Dimension

from app.src.services.sheets.creds import get_worksheet


async def get_data_from_sheet() -> list[list[str]]:
    ws = await get_worksheet()
    return await ws.get("B2:G100", major_dimension=Dimension.rows)
