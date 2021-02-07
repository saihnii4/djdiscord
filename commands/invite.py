import discord.ext.commands
import discord

@discord.ext.commands.command(name="invite", aliases=["inv"])
async def invite(ctx: discord.ext.commands.Context) -> None:
    await ctx.send("Check your DMs for the invite")
    return await ctx.author.send("https://discord.com/api/oauth2/authorize?client_id=788392608254787595&permissions=3197248&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fapi%2Fv1%2Fdiscord&scope=bot")

def setup(bot: discord.ext.commands.Bot):
    bot.add_command(invite)