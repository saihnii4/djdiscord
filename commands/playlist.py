import time
import typing
import uuid

import discord
import discord.ext.commands
import discord.ext.menus
import psutil
import rethinkdb
import youtube_dl

from utils.constants import Playlist, Song, ydl_opts, BeforeCogInvoke, AfterCogInvoke, Error
from utils.converters import IndexConverter
from utils.converters import PlaylistConverter
from utils.converters import PlaylistPaginator
from utils.converters import SongConverter
from utils.converters import VoicePrompt
from utils.converters import VolumeConverter
from utils.extensions import DJDiscordContext
from utils.voice import VoiceError, VoiceState


class PlaylistCommands(discord.ext.commands.Cog):
    async def cog_before_invoke(self, ctx: DJDiscordContext) -> None:
        memory_sample = psutil.virtual_memory()
        await ctx.database.log(
            BeforeCogInvoke(ctx.author, self, ctx.command, ctx.guild,
                            ctx.channel),
            {
                "cpu": psutil.cpu_percent(),
                "ram": memory_sample.used / memory_sample.total,
                "disk": psutil.disk_usage("/")
            })
        await ctx.trigger_typing()

    async def cog_after_invoke(self, ctx: DJDiscordContext) -> None:
        memory_sample = psutil.virtual_memory()
        await ctx.database.log(
            AfterCogInvoke(ctx.author, self, ctx.command, ctx.guild,
                           ctx.channel), {
                               "cpu": psutil.cpu_percent(),
                               "ram": memory_sample.used / memory_sample.total,
                               "disk": psutil.disk_usage("/")
                           })

    async def cog_command_error(self, ctx: DJDiscordContext,
                                error: Exception) -> None:
        memory_sample = psutil.virtual_memory()
        await ctx.database.log(
            Error(ctx.author, self, ctx.command, ctx.guild, ctx.channel), {
                "cpu": psutil.cpu_percent(),
                "ram": memory_sample.used / memory_sample.total,
                "disk": psutil.disk_usage("/")
            })

    @discord.ext.commands.group(name="playlist")
    async def playlist(
            self, ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if ctx.invoked_subcommand is None:
            notification = (ctx.bot.templates.incompleteCmd.copy(
            ).set_thumbnail(
                url="https://media4.giphy.com/media/TqiwHbFBaZ4ti/giphy.gif"
            ).set_author(name=ctx.author.name,
                         icon_url=ctx.author.avatar_url_as(
                             format="png")).set_footer(text="Unix Time: %d" %
                                                       time.time()))
            notification.description = notification.description.format(ctx)
            return await ctx.send(embed=notification)

    @playlist.command(name="volume")
    async def volume(self, ctx: DJDiscordContext,
                     volume: VolumeConverter) -> None:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to change the volume"
            )

        state = ctx.voice_queue.get(ctx.guild.id)

        state.voice.source.volume = volume

    @playlist.command(name="skip")
    async def skip(self,
                   ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to skip music")

        state = ctx.voice_queue.get(ctx.guild.id)

        state.skip()

        return await ctx.send(
            embed=discord.Embed(title="Skipped song!", color=0xA1D2CE))

    @playlist.command(name="loop")
    async def loop(self,
                   ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to skip music")

        state = ctx.voice_queue.get(ctx.guild.id)

        if state._loop:
            state._loop = False
            return

        state._loop = True

    @playlist.command(name="stop", aliases=["end", "interrupt", "sigint"])
    async def stop(self,
                   ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to stop music")

        state = ctx.voice_queue.get(ctx.guild.id)

        if len(state.voice.channel.members) <= 3:
            await ctx.send(embed=discord.Embed(
                title="Disconnected from the voice channel and stopped playing",
                color=0xA1D2CE))
            return await state.stop()

        if len(state.voice.channel.members) >= 3 and await ctx.dj:
            vote_count = await VoicePrompt("Stop the current song?").prompt(ctx
                                                                            )
            if vote_count >= 1:
                await state.stop()

    @playlist.command(name="start", aliases=["execute", "run"])
    async def execute(
        self,
        ctx: DJDiscordContext,
        playlist: PlaylistConverter,
        *,
        channel: discord.VoiceChannel = None
    ) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to start playing music"
            )

        if channel is None:
            channel = ctx.author.voice.channel

        target = channel if channel is not None else ctx.author.voice.channel

        state = ctx.voice_queue.get(ctx.guild.id)
        if not state:
            state = VoiceState(ctx.bot, ctx, playlist)
            ctx.voice_queue[ctx.guild.id] = state

        ctx.voice_state = state

        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(target)
            return

        state.voice = await target.connect()

        def recurse_play(song: Song) -> None:
            def handle_after(error) -> None:
                if error is None:
                    try:
                        ctx.voice_state.shift()
                        if ctx.voice_state.current is None:
                            raise StopIteration()
                        if ctx.voice_state.voice is None:
                            raise VoiceError()
                        return recurse_play(ctx.voice_state.current)
                    except Exception as error:
                        if isinstance(error, StopIteration):
                            ctx.bot.loop.create_task(
                                ctx.send(embed=discord.Embed(
                                    title="Finished playing this playlist!",
                                    color=0xA1D2CE)))
                            ctx.bot.loop.create_task(
                                ctx.voice_queue[ctx.guild.id].stop())
                            del ctx.voice_queue[ctx.guild.id]
                            return

                raise error

            with youtube_dl.YoutubeDL(ydl_opts) as ytdl:
                data = ytdl.extract_info(song["url"], download=False)
                song["source"] = data["formats"][0]["url"]

            ctx.bot.loop.create_task(
                ctx.send(embed=discord.Embed(
                    title="Current song in queue",
                    description=
                    "```css\n{} - {}\n\nCreated at {} - {} seconds long\n```".
                    format(song["title"], song["uploader"], song["created"],
                           song["length"]),
                    color=0xA1D2CE).set_thumbnail(
                        url=song["thumbnails"][-1]["url"])))

            ctx.voice_queue[ctx.guild.id].voice.play(
                discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                    song["source"]),
                                             volume=1),
                after=handle_after)

        recurse_play(ctx.voice_state.current)

    @playlist.command(name="delete")
    async def delete(self, ctx: DJDiscordContext,
                     indx: IndexConverter) -> typing.Optional[discord.Message]:
        if indx is None:
            return await ctx.send("You need to pick a number bigger than 0")
        playlist = await PlaylistConverter().convert(ctx, str(ctx.author.id))
        if len(playlist.songs) < indx:
            return await ctx.send("No such song exists at index %d" % indx)

        await ctx.send("Deleted **`%s`** from your playlist" %
                       playlist.songs[indx - 1]["title"])
        return await playlist.delete_at(ctx, indx)

    @playlist.command(name="list")
    async def list(self,
                   ctx: DJDiscordContext,
                   playlist: PlaylistConverter = None
                   ) -> typing.Optional[discord.Message]:
        if playlist is None:
            slot = await ctx.database.get(author=ctx.author.id)
            if not slot:
                return await ctx.send("You haven't created a playlist yet!")
            query = slot[0]
            playlist = Playlist(query["id"], query["songs"], query["author"],
                                query["cover"])
        paginator = discord.ext.menus.MenuPages(source=PlaylistPaginator(
            playlist.songs, ctx=ctx, playlist=playlist),
                                                clear_reactions_after=True)
        await paginator.start(ctx)

    @playlist.command(name="add")
    async def add(self, ctx: DJDiscordContext, *,
                  song: SongConverter) -> typing.Optional[discord.Message]:
        playlist = await PlaylistConverter().convert(ctx, str(ctx.author.id))
        message = ctx.bot.templates.playlistChange.copy()
        await playlist.add_song(ctx, song)
        return await ctx.send(embed=message.add_field(
            name="New Song!", value="%s {}".format(song.title) % song.emoji))

    @playlist.command(name="create")
    async def create(
            self, ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if await ctx.database.get(author=ctx.author.id):
            return await ctx.send("You already have a playlist")

        playlist_id = str(uuid.uuid4())
        await ctx.database.run(
            rethinkdb.r.table("playlists").insert({
                "id": playlist_id,
                "author": ctx.author.id,
                "songs": [],
                "upvotes": 0,
                "cover": None,
            }))

        msg = await ctx.send(embed=discord.Embed(
            title="Almost there!", color=0xDA3E52
        ).add_field(
            name="Cover Art",
            value=
            "Now upload your cover art, if you don't want to upload anything, ignore this message for 20 seconds",
        ).set_image(
            url=
            "https://cdn.discordapp.com/attachments/783142801294098474/800616441169838100/progress.gif"
        ))

        response = await ctx.wait_for(
            "message",
            check=lambda message: message.author == ctx.author,
            timeout=20)

        if response is None:
            return

        if not response.attachments:
            return await ctx.send(
                "You didn't send an attachment to set as your cover art, so we stopped listening"
            )

        await ctx.database.run(
            rethinkdb.r.table("playlists").filter({
                "id": playlist_id,
                "author": ctx.author.id
            }).update({"cover": response.attachments[0].url}))

        return await msg.edit(
            embed=discord.Embed(
                title="All done!",
                description=
                "Everything is clear! Begin adding songs to your playlist!",
                color=0xF2E94E).add_field(name="Playlist Code",
                                          value=playlist_id)
            # .add_field(name="Song Limit", value="%d" % 40 if ctx.author.premium else 20)
            .set_thumbnail(url=response.attachments[0].url).set_image(
                url=
                "https://cdn.discordapp.com/attachments/783142801294098474/800616839754678272/congrats.gif"
            ))


def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_cog(PlaylistCommands())
