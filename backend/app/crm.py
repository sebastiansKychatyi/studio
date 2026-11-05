"""CRM links on other records (cards, events, income, time): only the user's own client and project."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Client, Project, User


async def own_client(db: AsyncSession, user: User, client_id: int | None, project_id: int | None = None) -> None:
    if client_id is not None:
        c = await db.get(Client, client_id)
        if c is None or c.user_id != user.id:
            raise HTTPException(404, "Client not found")
    if project_id is not None:
        p = await db.get(Project, project_id)
        if p is None or p.user_id != user.id or (client_id is not None and p.client_id != client_id):
            raise HTTPException(404, "Project not found")
