from typing import List

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_crud
from app.schemas.charity_project import CharityProjectDB
from app.services.google_api import (set_user_permissions,
                                     spreadsheets_create,
                                     spreadsheet_update_value)


router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service),
):
    """Подготовка google-таблицы. Только для суперюзеров."""

    projects = await charity_crud.get_close_projects(
        session,
    )
    spreadsheetid = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreadsheetid, wrapper_services)
    await spreadsheet_update_value(
        spreadsheetid,
        projects,
        wrapper_services,
    )

    return projects