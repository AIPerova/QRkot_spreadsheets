from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase[Donation]):

    async def get_by_user(
        self,
        user: User,
        session: AsyncSession,
    ) -> List[Donation]:
        """Возвращает все инвестиции пользователя."""

        donations = await session.execute(select(Donation).where(
            Donation.user_id == user.id)
        )

        return donations.scalars().all()


donations_crud = CRUDDonation(Donation)