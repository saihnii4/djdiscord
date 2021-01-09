import datetime
import os

import discord.ext.commands
import rethinkdb

from utils.constants import Templates
from utils.database import DJDiscordDatabaseManager


class DJDiscordContext(discord.ext.commands.Context):
    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

    @property
    def voice_queue(self):
        return self.bot.voice_queue

    async def wait_for(self, event: str, check, timeout=10):
        try:
            return await self.bot.wait_for(event, check=check, timeout=timeout)
        except Exception:
            pass

    @property
    def database(self: discord.ext.commands.Context) -> DJDiscordDatabaseManager:
        return DJDiscordDatabaseManager(self.bot.connection)

class DJDiscord(discord.ext.commands.Bot):
    """DJDiscord [discord.ext.commands.Bot] -> Base class for DJ Discord"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice_queue = {}
        for object in os.listdir("./commands"):
            if os.path.isfile(
                "./commands/%s" % object
            ) and os.path.splitext(
                "./commands/%s" % object
            )[1] == ".py":
                self.load_extension("commands.%s" %
                                    os.path.splitext(object)[0])

    async def on_connect(self):
        rethinkdb.r.set_loop_type('asyncio')
        self.connection = await rethinkdb.r.connect(db="djdiscord", host=os.environ["RETHINKDB_HOST"],
                                                    port=os.environ["RETHINKDB_PORT"],
                                                    user=os.environ["RETHINKDB_USER"],
                                                    password=os.environ["RETHINKDB_PASS"])

    async def on_ready(self):
        print("DJDiscord has logged into Discord as %s\nTime: {}".format(datetime.datetime.now()) % str(self.user))

    async def process_commands(self: discord.ext.commands.Bot, message: discord.Message) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=DJDiscordContext)
        await self.invoke(ctx)

    @property
    def templates(self):
        return Templates
