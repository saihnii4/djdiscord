from datetime import datetime
import discord.ext.commands
import lavalink
import rethinkdb
import asyncpg
import discord


@discord.ext.commands.command(name="info", aliases=["about"])
async def info(ctx: discord.ext.commands.Context):
    return await ctx.send(embed=discord.Embed(
        title="About DJ Discord",
        color=0xDC333C,
        timestamp=datetime.now()
    ).add_field(
        name="quid est quod ego?",
        value="I came up with the idea on a stroll through a park, "
              "seeing that no one made a similar bot, I decided to make this."
    ).add_field(
        name="is it open source?",
        value="[yes](https://github.com/notduckduckcode/djdiscord)",
        inline=False
    ).add_field(
        name="libraries/frameworks used",
        value="> rethinkdb - database/playlist storage v{0}\n"
              "> postgresql - configuration (will be removed in next version) v{1}\n"
              "> lavalink.py - lavalink for discord.py / voice v{2}".format(
                  rethinkdb.__version__, asyncpg.__version__, lavalink.__version__),
        inline=False
    ).add_field(name="about the owner", value="they exist"))

def setup(bot: discord.ext.commands.Bot):
    bot.add_command(info)
