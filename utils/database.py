import rethinkdb

class DJDiscordDatabaseManager:
    def __init__(self, rdbconn: any, psqlconn: any) -> None:
        self.rdbconn = rdbconn
        self.psqlconn = psqlconn

    async def get(self, **kwargs) -> list:
        """**`[coroutine]`** get -> Fetch accounts that fit a keyword argument"""

        return [obj async for obj in await rethinkdb.r.database("djdiscord").table("accounts").filter(kwargs).run(self.rdbconn)]
