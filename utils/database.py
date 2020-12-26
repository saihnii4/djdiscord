import rethinkdb

class DJDiscordDatabaseManager:
    def __init__(self, connection: any) -> None:
        self.connection = connection
        self.database = rethinkdb.r.db("djdiscord")

    async def get(self, **kwargs) -> list:
        """**`[coroutine]`** get -> Fetch accounts that fit a keyword argument"""

        return [obj async for obj in await self.database.table("accounts").filter(kwargs).run(self.connection)]

    @property
    async def playlists(self) -> any:
        return self.database.table("playlists")