import discord.ext.commands
import psutil
import discord

from utils.voice import VoiceState
from utils.converters import StationConverter
from utils.constants import BeforeCogInvoke, AfterCogInvoke, Error
from utils.extensions import DJDiscordContext

class RadioCog(discord.ext.commands.Cog):
    async def cog_before_invoke(self, ctx: DJDiscordContext) -> None:
        memory_sample = psutil.virtual_memory()
        await ctx.database.log(
            BeforeCogInvoke(ctx.author, self, ctx.command, ctx.guild, ctx.channel),
            {
                "cpu": psutil.cpu_percent(),
                "ram": memory_sample.used / memory_sample.total,
                "disk": psutil.disk_usage("/"),
            },
        )
        await ctx.trigger_typing()

    async def cog_after_invoke(self, ctx: DJDiscordContext) -> None:
        memory_sample = psutil.virtual_memory()
        await ctx.database.log(
            AfterCogInvoke(ctx.author, self, ctx.command, ctx.guild, ctx.channel),
            {
                "cpu": psutil.cpu_percent(),
                "ram": memory_sample.used / memory_sample.total,
                "disk": psutil.disk_usage("/"),
            },
        )

    async def cog_command_error(self, ctx: DJDiscordContext, error: Exception) -> None:
        memory_sample = psutil.virtual_memory()
        await ctx.database.log(
            Error(ctx.author, self, ctx.command, ctx.guild, ctx.channel),
            {
                "cpu": psutil.cpu_percent(),
                "ram": memory_sample.used / memory_sample.total,
                "disk": psutil.disk_usage("/"),
            },
            error
        )

    @discord.ext.commands.group(name="radio")
    async def radio(self, ctx: discord.ext.commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            # insert...
            pass

    @radio.command
    async def start(self, ctx: discord.ext.commands.Context, station: StationConverter, channel: discord.VoiceChannel = None) -> None:
        # insert...
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to start playing music"
            )

        if channel is None:
            channel = ctx.author.voice.channel

        target = channel if channel is not None else ctx.author.voice.channel

        state = ctx.voice_queue.get(ctx.guild.id)
        if not state:
            state = VoiceState(ctx.bot, ctx, station)
            ctx.voice_queue[ctx.guild.id] = state

        ctx.voice_state = state

        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(target)
            return

        state.voice = await target.connect()

        def handle_after(error) -> None:
            if error:
                raise error

            ctx.bot.loop.create_task(state.stop())

        ctx.voice_queue[ctx.guild.id].voice.play(
                discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(station["source"]), volume=1
                ),
                after=handle_after,
        )

    @radio.command
    async def stop(self, ctx: discord.ext.commands.Context) -> None:
        # insert...
        pass

    @radio.command
    async def volume(self, ctx: discord.ext.commands.Context) -> None:
        # insert...
        pass

    @radio.command
    async def info(self, ctx: discord.ext.commands.Context) -> None:
        # insert...
        pass

def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_cog(RadioCog())
