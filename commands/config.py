import discord.ext.commands
from utils.converters import ArgumentConverter

@discord.ext.commands.group(name="config", alises=["configuration"])
async def config(ctx: discord.ext.commands.Context, *, args: ArgumentConverter) -> None:
    arguments = vars(args)
    return await ctx.send(arguments)

def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_command(config)