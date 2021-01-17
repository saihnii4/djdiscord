from utils.constants import TableEvaluation
from utils.constants import DatabaseEvaluation
from utils.constants import DocumentEvaluation
import rethinkdb
import asyncpg
import typing

class DJDiscordDatabaseManager:
    def __init__(self, rdbconn: rethinkdb.net.Connection, psqlconn: asyncpg.Connection) -> None:
        self.rdbconn = rdbconn
        self.psqlconn = psqlconn

    async def _rethinkdbExecute(self, query) -> typing.Union[TableEvaluation, DatabaseEvaluation, DocumentEvaluation, dict, list]:
        result = await query.run(self.rdbconn)
        if isinstance(query, (rethinkdb.ast.TableCreate, rethinkdb.ast.TableDrop)):
            return TableEvaluation.from_dict(result)

        if isinstance(query, (rethinkdb.ast.DbDrop, rethinkdb.ast.DbDrop)):
            return DatabaseEvaluation.from_dict(result)

        if isinstance(query, (rethinkdb.ast.Delete, rethinkdb.ast.Update, rethinkdb.ast.Insert)):
            return DocumentEvaluation.from_dict(result)

        return result

    async def _psqlExecute(self, query, *args, **kwargs) -> None:
        await self.psqlconn.execute(query, *args, **kwargs)

    async def run(self, query, *args, **kwargs):
        if isinstance(query, str):
            return await self._psqlExecute(query, *args, **kwargs)

        return await self._rethinkdbExecute(query)

    async def get(self, **kwargs) -> list:
        """**`[coroutine]`** get -> Fetch accounts that fit a keyword argument"""

        return [obj async for obj in await rethinkdb.r.table("accounts").filter(kwargs).run(self.rdbconn)]
