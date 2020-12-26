import datetime
import rethinkdb
import discord.ext.commands
import asyncio
import discord
import dotenv
import os

dotenv.load_dotenv()


class Database(type):
    """Database type"""


class DJDB(metaclass=Database):
    def __init__(self, connection: any) -> None:
        self.connection = connection
        self.database = rethinkdb.r.db("djdiscord")

    async def get(self, _: discord.ext.commands.Context, **kwargs) -> list:
        """`[coro]` get -> Fetch accounts that fit a keyword argument"""

        return [obj async for obj in await self.database.table("accounts").filter(kwargs).run(self.connection)]

    @property
    async def accounts(self) -> any:
        return self.database.table("accounts")


class Template(type):
    """Template type"""


class Templates(metaclass=Template):
    eval = discord.Embed(title="Evaluation Complete!",
                         description="Evaluations are closely monitored for data leaks and as such this message "
                         "will self destruct in 10 seconds", color=4128651)

    incompleteCmd = discord.Embed(title="**`ERROR`** - Insufficent Arguments",
                                  description="Or in layman's terms, you need to give a bit more for this to work\n```\nUsage:\n{0.bot.command_prefix}{0.command.name} <command> <arguments>\n```")
    cmdError = discord.Embed(title="**`ERROR`** - Internal Error", description="Or in layman's terms, you may need to tell the developers about this\n```\n{}```").set_image(
        url="https://media4.giphy.com/media/TqiwHbFBaZ4ti/giphy.gif")
    playlistChange = discord.Embed(title="Done!", description="Feel free to share this playlist with your friends!",
                                   color=0x3EFF8B)
    playlistPaginator = discord.Embed(title="Songs in `{}`", description="Playlist ID: {}", color=0xE9B44C)
    playlistsPaginator = discord.Embed(title="Songs for `{}`", description="Total: {} playlists", color=0xF2DDA4)

class DJDiscordContext(discord.ext.commands.Context):
    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

    async def wait_for(self, event: str, check, timeout=10):
        try:
            return await self.bot.wait_for(event, check=check, timeout=timeout)
        except Exception:
            pass

    @property
    def database(self: discord.ext.commands.Context) -> DJDB:
        return DJDB(self.bot.connection)

class DJDiscord(discord.ext.commands.Bot):
    """DJDiscord [discord.ext.commands.Bot] -> Base class for DJ Discord"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command("help")
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
        self.connection = await rethinkdb.r.connect(db="djdiscord", host=os.environ["RETHINKDB_HOST"], port=os.environ["RETHINKDB_PORT"], user=os.environ["RETHINKDB_USER"], password=os.environ["RETHINKDB_PASS"])

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


bot = DJDiscord(command_prefix="!")

bot.run(os.environ["BOT_TOKEN"])
