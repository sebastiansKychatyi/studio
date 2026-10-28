"""User management (there is no public sign-up).

    python -m app.cli add sebastian --name "Sebastian"
    python -m app.cli passwd sebastian
    python -m app.cli list
    python -m app.cli remove roman
"""

import argparse
import asyncio
import getpass
import sys

from sqlalchemy import delete, func, select

from .db import SessionLocal, engine
from .models import Base, Session, User
from .security import hash_password


def _ask_password() -> str:
    while True:
        pw = getpass.getpass("Password: ")
        if len(pw) < 8:
            print("At least 8 characters.")
        elif len(pw.encode()) > 72:
            print("Max 72 bytes (bcrypt limit).")
        elif pw != getpass.getpass("Repeat: "):
            print("Passwords do not match.")
        else:
            return pw


async def _find(db, username: str) -> User | None:
    return await db.scalar(select(User).where(func.lower(User.username) == username.lower()))


async def main(args: argparse.Namespace) -> int:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        if args.cmd == "list":
            for u in (await db.scalars(select(User).order_by(User.id))).all():
                print(f"{u.id:>3}  {u.username:<20} {u.name}")
            return 0

        user = await _find(db, args.username)
        if args.cmd == "add":
            if user:
                print(f"User '{args.username}' already exists.")
                return 1
            db.add(User(username=args.username.lower(), name=args.name or args.username, password_hash=hash_password(_ask_password())))
        elif user is None:
            print(f"User '{args.username}' not found.")
            return 1
        elif args.cmd == "passwd":
            user.password_hash = hash_password(_ask_password())
            # Log out everywhere
            await db.execute(delete(Session).where(Session.user_id == user.id))
        elif args.cmd == "remove":
            await db.delete(user)
        await db.commit()
        print("Done.")
    await engine.dispose()
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(prog="python -m app.cli")
    sub = p.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add", help="create a user")
    add.add_argument("username")
    add.add_argument("--name", default="")
    sub.add_parser("passwd", help="change password").add_argument("username")
    sub.add_parser("remove", help="delete a user").add_argument("username")
    sub.add_parser("list", help="list users")
    sys.exit(asyncio.run(main(p.parse_args())))
