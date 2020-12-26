import textwrap
import discord.ext.commands
import discord


@discord.ext.commands.command(name="help")
async def help(ctx: discord.ext.commands.Context) -> None:
    payload = discord.Embed(
        title="DJ Discord",
        description=textwrap.dedent("""
                                    ```
                                    DJ Discord - The one music bot to rule them all"
                                    {}\nv0.1.0-a.1
                                    playlists
                                    ```
                                    """.format(ctx.bot.__logo__)))

    return await ctx.send(embed=payload)


def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_command(help)
