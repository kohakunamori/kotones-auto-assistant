import os
import sqlite3
from typing import Any, cast

from kotonebot.kaa import resources as res

_db: sqlite3.Connection | None = None
_db_path = cast(str, res.__path__)[0] + '/game.db'

def select_many(query: str, *args) -> list[Any]:
    global _db
    if not _db:
        _db = sqlite3.connect(_db_path)
    c = _db.cursor()
    c.execute(query, args)
    return c.fetchall()


def select(query: str, *args) -> Any:
    global _db
    if not _db:
        _db = sqlite3.connect(_db_path)
    c = _db.cursor()
    c.execute(query, args)
    return c.fetchone()