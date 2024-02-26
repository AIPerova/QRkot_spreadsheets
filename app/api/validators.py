from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT
from app.crud.charity_project import charity_crud
from app.models import CharityProject


async def check_project(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    """Поиск проекта по id."""

    project = await charity_crud.get(
        obj_id=project_id,
        session=session,
    )
    if not project:

        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!',
        )

    return project


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    """Проверка имени проекта на уникальность."""

    project_id = await charity_crud.get_project_by_name(
        project_name,
        session,
    )
    if project_id is not None:

        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_closed(
        project_id: int,
        session: AsyncSession,
) -> None:
    """Проверка закрыт ли проект."""

    project = await charity_crud.get(
        obj_id=project_id,
        session=session,
    )
    if project.fully_invested:

        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )


async def check_donations_in_project(
        project_id: int,
        session: AsyncSession,
) -> None:
    """Проверка наличия инвестиций в проект."""

    project = await charity_crud.get(
        obj_id=project_id,
        session=session,
    )
    if project.invested_amount > DEFAULT:

        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )


async def check_sum_change(
        new_sum: int,
        project_id: int,
        session: AsyncSession,
) -> None:
    """Проверка корректности суммы(нельзя изменить сумму на меньшую)."""

    project = await charity_crud.get(
        obj_id=project_id,
        session=session,
    )
    if new_sum < project.invested_amount:

        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Нельзя установить сумму меньше инвестированной!',
        )