from __future__ import annotations

import os

import asyncpg
import discord
import discord.ext.commands
import rethinkdb

from utils.objects import Templates
from utils.database import DJDiscordDatabaseManager


class DJDiscordContext(discord.ext.commands.Context):
    def __init__(self: DJDiscordContext, **kwargs: dict) -> None:
        super().__init__(**kwargs)

    @property
    def voice_queue(self: DJDiscordContext) -> dict:
        return self.bot.voice_queue

    @property
    async def dj(self: DJDiscordContext):
        role_id = await self.database.psqlconn.fetch(
            """SELECT (dj_role) FROM configuration WHERE id=$1""",
            self.guild.id)

        role = discord.utils.get(self.guild.roles, id=role_id)

        return role in self.author.roles

    async def wait_for(self: DJDiscordContext, event: str, check, timeout=10):
        try:
            return await self.bot.wait_for(event, check=check, timeout=timeout)
        except Exception:
            pass

    @property
    def database(
            self: DJDiscordContext) -> DJDiscordDatabaseManager:
        return DJDiscordDatabaseManager(self.bot.rdbconn, self.bot.psqlconn)


class DJDiscord(discord.ext.commands.Bot):
    """DJDiscord [discord.ext.commands.Bot] -> Base class for DJ Discord"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice_queue = {}
        for object in os.listdir("./commands"):
            if os.path.isfile("./commands/%s" % object) and os.path.splitext(
                    "./commands/%s" % object)[1] == ".py":
                self.load_extension("commands.%s" %
                                    os.path.splitext(object)[0])

    async def on_connect(self):
        rethinkdb.r.set_loop_type('asyncio')
        self.rdbconn = await rethinkdb.r.connect(
            db="djdiscord",
            host=os.environ["RETHINKDB_HOST"],
            port=os.environ["RETHINKDB_PORT"],
            user=os.environ["RETHINKDB_USERNAME"],
            password=os.environ["RETHINKDB_PASSWORD"])
        self.psqlconn = await asyncpg.connect(
            user=os.environ["POSTGRESQL_USERNAME"],
            password=os.environ["POSTGRESQL_PASSWORD"],
            database="djdiscord_config",
            host=os.environ["POSTGRESQL_HOST"],
            port=os.environ["POSTGRESQL_PORT"])

    async def on_ready(self):
        print("Ready!")

    async def process_commands(self: discord.ext.commands.Bot,
                               message: discord.Message) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=DJDiscordContext)
        await self.invoke(ctx)

    @property
    def templates(self):
        return Templates
