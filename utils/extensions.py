from __future__ import annotations
import asyncio

import os

import asyncpg
import lavalink
import discord
import rethinkdb
import async_spotify
import discord.ext.commands
import async_spotify.authentification.authorization_flows

from pretty_help import PrettyHelp
from utils.objects import Templates
from utils.database import DJDiscordDatabaseManager

rethinkdb.r.set_loop_type("asyncio")


class DJDiscordContext(discord.ext.commands.Context):
    def __init__(self: DJDiscordContext, **kwargs: dict) -> None:
        super().__init__(**kwargs)

    @property
    def spotify(self: DJDiscordContext) -> async_spotify.SpotifyApiClient:
        return self.bot.spotify_api_client

    @property
    def player(self: DJDiscordContext) -> None:
        if not self.bot.lavalink.player_manager.get(self.guild.id):
            player = self.bot.lavalink.player_manager.create(
                self.guild.id, endpoint=str(self.guild.region))
            return player
        return self.bot.lavalink.player_manager.get(self.guild.id)

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
    def database(self: DJDiscordContext) -> DJDiscordDatabaseManager:
        return DJDiscordDatabaseManager(self.bot.rdbconn, self.bot.psqlconn)


class DJDiscord(discord.ext.commands.Bot):
    """DJDiscord [discord.ext.commands.Bot] -> Base class for DJ Discord"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         **kwargs,
                         help_command=PrettyHelp(
                             dm_help=False,
                             color=0xDC333C,
                             no_category="General Commands",
                             index_title="DJDiscord Commands",
                             show_index=False,
                         ))
        self.voice_queue = {}
        for object in os.listdir("./commands"):
            if (os.path.isfile("./commands/%s" % object) and os.path.splitext(
                    "./commands/%s" % object)[1] == ".py"):
                self.load_extension("commands.%s" %
                                    os.path.splitext(object)[0])
        self.load_extension("jishaku")
        self.loop.create_task(self.update_presence())

    async def update_presence(self) -> None:
        await self.wait_until_ready()
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.competing,
            name="{} server{}. Prefix: dj;".format(
                len(self.guilds), "" if len(self.guilds) == 1 else "s"),
        ))
        await asyncio.sleep(120)

    async def on_connect(self):
        self.lavalink = lavalink.Client(self.user.id)
        self.lavalink.add_node(
            os.environ["LAVALINK_HOST"],
            os.environ["LAVALINK_PORT"],
            os.environ["LAVALINK_PASSWORD"],
            os.environ["LAVALINK_REGION"],
            os.environ["LAVALINK_NODE_NAME"],
        )
        self.add_listener(self.lavalink.voice_update_handler,
                          "on_socket_response")
        auth_flow = async_spotify.authentification.authorization_flows.ClientCredentialsFlow(
            application_id=os.environ["SPOTIPY_CLIENT_ID"],
            application_secret=os.environ["SPOTIPY_CLIENT_SECRET"])
        auth_flow.load_from_env()
        self.spotify_api_client = async_spotify.SpotifyApiClient(
            auth_flow, hold_authentication=True)
        await self.spotify_api_client.get_auth_token_with_client_credentials()
        await self.spotify_api_client.create_new_client()
        self.rdbconn = await rethinkdb.r.connect(
            db="djdiscord",
            host=os.environ["RETHINKDB_HOST"],
            port=os.environ["RETHINKDB_PORT"],
            user=os.environ["RETHINKDB_USERNAME"],
            password=os.environ["RETHINKDB_PASSWORD"],
        )
        self.psqlconn = await asyncpg.connect(
            user=os.environ["POSTGRESQL_USERNAME"],
            password=os.environ["POSTGRESQL_PASSWORD"],
            database="djdiscord_config",
            host=os.environ["POSTGRESQL_HOST"],
            port=os.environ["POSTGRESQL_PORT"],
        )

    async def on_ready(self):
        print("Ready!")

    async def on_message(self, message):
        if not message.author.bot and "<@!788392608254787595>" in message.content:
            return await message.channel.send("My prefix is dj;")

        return await self.process_commands(message)

    async def process_commands(self: discord.ext.commands.Bot,
                               message: discord.Message) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=DJDiscordContext)
        await self.invoke(ctx)

    @property
    def templates(self):
        return Templates
