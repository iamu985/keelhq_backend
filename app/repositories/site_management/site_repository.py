from typing import Optional, Sequence

from sqlmodel import delete, select
from app.db.models import Site
from sqlalchemy.ext.asyncio import AsyncSession


class SiteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, site: Site) -> Site:
        self.session.add(site)
        await self.session.flush()
        await self.session.refresh(site)
        return site

    async def get(self, site_id: str) -> Optional[Site]:
        stmt = select(Site).where(Site.id == site_id)
        result = await self.session.execute(stmt)
        site = result.scalar_one_or_none()
        return site

    async def list(self) -> Sequence[Site]:
        stmt = select(Site)
        result = await self.session.execute(stmt)
        sites = result.scalars().all()
        return sites

    async def delete(self, site: Site) -> Site:
        await self.session.delete(site)
        await self.session.flush()
        return site
