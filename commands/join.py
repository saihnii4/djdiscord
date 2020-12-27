from utils.constants import VoiceState
from commands.playlist import start
import discord.ext.commands
import typing

@discord.ext.commands.command(name="join")
@start.before_invoke
async def join(ctx: discord.ext.commands.Context,
               *,
               channel: discord.VoiceChannel = None
               ) -> typing.Optional[discord.Message]:
    if ctx.author.voice is None:
        return await ctx.send(
            "You have not joined a voice channel yet, therefore you cannot play music"
        )

    target = channel if channel is not None else ctx.author.voice.channel

    state = ctx.voice_queue.get(ctx.guild.id)
    if not state:
        state = VoiceState(ctx.bot, ctx)
        ctx.voice_queue[ctx.guild.id] = state

    ctx.voice_state = state

    if ctx.voice_state.voice:
        await ctx.voice_state.voice.move_to(target)
        return

    state.voice = await target.connect()

def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_command(join)
