from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_donations_in_project,
    check_name_duplicate,
    check_project,
    check_project_closed,
    check_sum_change,
)
from app.api.utils import donate
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_crud
from app.crud.donation import donations_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)


router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """Возвращение списка проектов."""

    return await charity_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Добавление проекта. Только для суперюзера."""

    await check_name_duplicate(project.name, session)
    new_project = await charity_crud.create(project, session)
    await donate(new_project, donations_crud, session)

    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Изменение проекта. Только для суперюзера."""

    await check_project_closed(project_id, session)
    if obj_in.full_amount:
        await check_sum_change(obj_in.full_amount, project_id, session)
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    project = await check_project(
        project_id,
        session,
    )
    project = await charity_crud.update(
        db_obj=project,
        obj_in=obj_in,
        session=session,
    )
    await donate(project, donations_crud, session)

    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Удаление проекта. Только для суперюзера."""

    project = await check_project(
        project_id,
        session,
    )
    await check_donations_in_project(project_id, session)
    return await charity_crud.remove(project, session)
