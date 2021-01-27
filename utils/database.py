import traceback
import typing

import asyncpg
import rethinkdb
import rethinkdb.ast
import rethinkdb.net

from utils.constants import AfterCogInvoke
from utils.constants import AfterCommandInvoke
from utils.constants import BeforeCogInvoke
from utils.constants import BeforeCommandInvoke
from utils.constants import DatabaseEvaluation
from utils.constants import DocumentEvaluation
from utils.constants import TableEvaluation


class DJDiscordDatabaseManager:
    def __init__(self, rdbconn: rethinkdb.net.Connection,
                 psqlconn: asyncpg.Connection) -> None:
        self.rdbconn = rdbconn
        self.psqlconn = psqlconn

    async def _rethinkdb_execute(
        self, query
    ) -> typing.Union[TableEvaluation, DatabaseEvaluation, DocumentEvaluation,
                      dict, list]:
        result = await query.run(self.rdbconn)

        if isinstance(query,
                      (rethinkdb.ast.TableCreate, rethinkdb.ast.TableDrop)):
            return TableEvaluation.from_dict(result)

        if isinstance(query, (rethinkdb.ast.DbDrop, rethinkdb.ast.DbCreate)):
            return DatabaseEvaluation.from_dict(result)

        if isinstance(query, (rethinkdb.ast.Delete, rethinkdb.ast.Update,
                              rethinkdb.ast.Insert)):
            return DocumentEvaluation.from_dict(result)

        return result

    async def _psql_execute(self, query, *args, **kwargs) -> str:
        return await self.psqlconn.execute(query, *args, **kwargs)

    async def run(self, query, *args, **kwargs):
        if isinstance(query, str):
            return await self._psql_execute(query, *args, **kwargs)

        return await self._rethinkdb_execute(query)

    async def log(
        self,
        ctx: discord.ext.commands.Context,
        op: typing.Union[BeforeCogInvoke, AfterCogInvoke, BeforeCommandInvoke,
                         AfterCommandInvoke],
        info,
        error: Exception = None,
    ) -> DocumentEvaluation:

        payload = {"op": int(op), "info": info, "logged_at": rethinkdb.r.now()}

        if error := getattr(error, "original", error):
            payload.update({
                "error":
                "".join(
                    traceback.TracebackException.from_exception(
                        error).format()).strip()
            })

        return await self.run(
            rethinkdb.r.db("djdiscord").table("logs").insert(payload))

    async def get(self, **kwargs) -> list:
        """**`[coroutine]`** get -> Fetch accounts that fit a keyword argument"""

        return [
            obj async for obj in await rethinkdb.r.table(
                kwargs.get("table", "playlists")).filter(kwargs).run(
                    self.rdbconn)
        ]
