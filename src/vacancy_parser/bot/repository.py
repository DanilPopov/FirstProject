from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select

from vacancy_parser.config import settings
from vacancy_parser.db.models import User, UserFilter
from vacancy_parser.db.session import AsyncSessionFactory


async def get_or_create_user(tg_id: int, username: str | None) -> User:
    async with AsyncSessionFactory() as session:
        user = await session.get(User, tg_id)
        if user is None:
            user = User(
                id=tg_id,
                username=username,
                trial_ends_at=datetime.utcnow() + timedelta(hours=settings.trial_duration_hours),
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif user.username != username:
            user.username = username
            await session.commit()
        return user


async def save_filter(user_id: int, draft: dict) -> UserFilter:
    """Deactivate previous filters for this user and create a new active one."""
    async with AsyncSessionFactory() as session:
        existing = await session.execute(
            select(UserFilter).where(UserFilter.user_id == user_id, UserFilter.active.is_(True))
        )
        for f in existing.scalars():
            f.active = False

        f = UserFilter(
            user_id=user_id,
            name=draft.get("name", "default"),
            active=True,
            schedule=draft.get("schedule") or None,
            employment=draft.get("employment") or None,
            experience=draft.get("experience") or None,
            professional_roles=draft.get("professional_roles") or None,
            industry=draft.get("industry") or None,
            area=draft.get("area") or None,
            text=draft.get("text") or None,
            salary_min=draft.get("salary_min"),
            currency=draft.get("currency"),
        )
        session.add(f)
        await session.commit()
        await session.refresh(f)
        return f
