import gspread_asyncio
from google.oauth2.service_account import Credentials

from app.settings import settings


def get_creds():
    creds = Credentials.from_service_account_file("creds.json")
    return creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


async def get_worksheet() -> gspread_asyncio.AsyncioGspreadWorksheet:
    agc = await agcm.authorize()
    spreadsheet = await agc.open_by_key(settings.TABLE_KEY)
    return await spreadsheet.get_worksheet(1)

