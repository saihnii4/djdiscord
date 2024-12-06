import discord.ext.commands

from utils.convert import ArgumentConverter
from utils.extensions import DJDiscordContext


@discord.ext.commands.group(name="config", alises=["configuration"])
async def config(
        ctx: DJDiscordContext,
        *,
        args: ArgumentConverter = ArgumentConverter.defaults()) -> None:
    if not await ctx.database.psqlconn.fetch(
            """SELECT (id) FROM configuration WHERE id=$1""", ctx.guild.id):
        dj = discord.utils.get(ctx.guild.roles, name="DJ")
        announcement = discord.utils.get(ctx.guild.channels,
                                         name="announcements")
        await ctx.database.run(
            """INSERT INTO configuration (id, announcement, dj_role) VALUES ($1, $2, $3)""",
            ctx.guild.id,
            announcement.id if announcement is not None else announcement,
            dj.id if dj is not None else dj,
        )
    for key, value in args.items():
        if key not in (
                "announcement",
                "dj_role",
        ):
            continue

        if value is not None:
            await ctx.database.run(
                """UPDATE configuration SET {}=$1 WHERE ID=$2;""".format(key),
                value.id if value is not None else value, ctx.guild.id)

    return await ctx.send(args)


def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_command(config)
