from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.core.constants import COLUMN_COUNT, DEFAULT, DATE_FORMAT, ROW_COUNT


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
) -> str:
    now_date_time = datetime.now().strftime(DATE_FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {
            'title': f'Отчёт от {now_date_time}',
            'locale': 'ru_RU',
        },
        'sheets': [{
            'properties': {
                'sheetType': 'GRID',
                'sheetId': DEFAULT,
                'title': 'Лист1',
                'gridProperties': {
                    'rowCount': ROW_COUNT,
                    'columnCount': COLUMN_COUNT,
                }
            }
        }]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId']


async def set_user_permissions(
    spreadsheetid: str,
    wrapper_services: Aiogoogle,
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields='id',
        )
    )


async def spreadsheet_update_value(
        spreadsheetid: str,
        projects: list,
        wrapper_services: Aiogoogle,
) -> None:
    now_date_time = datetime.now().strftime(DATE_FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        [f'Отчёт от {now_date_time}'],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание'],
    ]
    for project in projects:
        time = project.close_date - project.create_date
        days = time.days
        new_row = [
            project.name,
            f'{days} days, {time}',
            project.description,
        ]
        table_values.append(new_row)
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values,
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )