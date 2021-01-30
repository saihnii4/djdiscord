import time
import typing
import re
import uuid

import discord
import discord.ext.commands
import discord.ext.menus
import rethinkdb
import youtube_dl

from utils.objects import (
    Playlist,
    Song,
    ydl_opts,
    BeforeCogInvokeOp,
    AfterCogInvokeOp,
    ErrorOp,
)
import lavalink
from utils.convert import IndexConverter
from utils.convert import PlaylistConverter
from utils.convert import PlaylistPaginator
from utils.convert import SongConverter
from utils.convert import VoicePrompt
from utils.convert import VolumeConverter
from utils.extensions import DJDiscordContext
from utils.voice import VoiceError, VoiceState


class PlaylistCommands(discord.ext.commands.Cog):
    async def cog_before_invoke(self, ctx: DJDiscordContext) -> None:
        if ctx.guild is None:
            return

        await self.ensure_voice(ctx)

        await ctx.database.log(
            BeforeCogInvokeOp(ctx.author, self, ctx.command, ctx.guild,
                              ctx.channel), )
        await ctx.trigger_typing()

    async def cog_after_invoke(self, ctx: DJDiscordContext) -> None:
        await ctx.database.log(
            AfterCogInvokeOp(ctx.author, self, ctx.command, ctx.guild,
                             ctx.channel), )

    async def cog_command_error(self, ctx: DJDiscordContext,
                                error: Exception) -> None:
        _id = uuid.uuid4()
        await ctx.database.log(ErrorOp(ctx.guild, ctx.channel, ctx.message,
                                       ctx.author),
                               error=error,
                               case_id=_id)
        print(f"An error occurred during command runtime. Case ID: {_id.hex}")

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = ctx.bot.lavalink.player_manager.create(ctx.guild.id,
                                                        endpoint=str(
                                                            ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise discord.ext.commands.CommandInvokeError(
                'Join a voicechannel first.')

        if not player.is_connected:
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise discord.ext.commands.CommandInvokeError(
                    'I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx, ctx.guild.id,
                                  str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise discord.ext.commands.CommandInvokeError(
                    'You need to be in my voicechannel.')

    async def track_hook(self, ctx, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)
            await self.connect_to(ctx, guild_id, None)

    async def connect_to(self, ctx, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = ctx.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    @discord.ext.commands.command(aliases=['p'])
    async def test(self, ctx, *, query: str):
        """ Searches and plays a song from a given query. """
        # Get the player for this guild from cache.
        player = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.

        url_rx = re.compile(r'https?://(?:www\.)?.+')
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # ALternatively, resullts['tracks'] could be an empty array if the query yielded no tracks.
        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        embed = discord.Embed(color=discord.Color.blurple())

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            print(tracks)

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            print(track)
            embed.title = 'Track Enqueued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.
            track = lavalink.models.AudioTrack(track,
                                               ctx.author.id,
                                               recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    @discord.ext.commands.command(name="now")
    async def now(self, ctx: DJDiscordContext) -> None:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to join a voice channel to see the current song in the queue"
            )

        if ctx.guild.id not in ctx.voice_queue:
            return await ctx.send("The bot isn't playing any music")

        current_obj = ctx.voice_queue[ctx.guild.id].current

        if "created" in current_obj:
            await ctx.send(
                embed=discord.Embed(title="Current song in queue").add_field(
                    name="Song Name", value=current_obj["title"]).add_field(
                        name="Song Length", value=current_obj["length"]).
                add_field(name="Song Uploader", value=current_obj["uploader"]).
                add_field(name="Original Link",
                          value="[Click Me!]({})".format(
                              current_obj["url"])).set_thumbnail(
                                  url=current_obj["thumbnails"][-1]["url"]))
        else:
            await ctx.send(embed=discord.Embed(
                title="Current radio station").add_field(
                    name="Radio Station Call Sign",
                    value=current_obj["call_sign"]).add_field(
                        name="Radio station Frequency",
                        value=current_obj["frequency"]).add_field(
                            name="Original Link", value=current_obj["url"]).
                           set_thumbnail(url=current_obj["thumbnail"]))

    @discord.ext.commands.command(name="volume")
    async def volume(self, ctx: DJDiscordContext,
                     volume: VolumeConverter) -> None:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to change the volume"
            )

        if ctx.guild.id not in ctx.voice_queue:
            return await ctx.send("The bot isn't playing any music")

        state = ctx.voice_queue.get(ctx.guild.id)

        state.voice.source.volume = volume

    @discord.ext.commands.command(name="skip")
    async def skip(self,
                   ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to skip music")

        state = ctx.voice_queue.get(ctx.guild.id)

        state.skip()

        return await ctx.send(
            embed=discord.Embed(title="Skipped song!", color=0xA1D2CE))

    @discord.ext.commands.command(name="loop")
    async def loop(self,
                   ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to skip music")

        if ctx.guild.id not in ctx.voice_queue:
            return await ctx.send("The bot isn't playing any music")

        state = ctx.voice_queue.get(ctx.guild.id)

        state._loop = not state._loop

    @discord.ext.commands.command(name="stop",
                                  aliases=["end", "interrupt", "sigint"])
    async def stop(self,
                   ctx: DJDiscordContext) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to stop music")
        player = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.author.voice or (
                player.is_connected
                and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voicechannel!')

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx, ctx.guild.id, None)
        return await ctx.send(embed=discord.Embed(
            title="Disconnected from the voice channel and stopped playing",
            color=0xA1D2CE,
        ))

    @discord.ext.commands.command(name="start", aliases=["begin", "play"])
    async def run(
        self,
        ctx: DJDiscordContext,
        playlist: PlaylistConverter = None,
    ) -> typing.Optional[discord.Message]:
        if ctx.author.voice is None:
            return await ctx.send(
                "You need to be connected to a channel in order to start playing music"
            )

        if playlist is None:
            playlist = (await ctx.database.get(author=ctx.author.id))[0]
            if playlist is None:
                return await ctx.send(
                    "You do not own a playlist nor have specified a playlist to start playing"
                )
            playlist = Playlist.from_json(playlist)

        player = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

        for song in playlist.songs:
            results = await player.node.get_tracks(song["url"])

            player.add(requester=ctx.author.id, track=results["tracks"][0])

        if not player.is_playing:
            await player.play()

    @discord.ext.commands.command(name="delete", aliases=["tremove"])
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

    @discord.ext.commands.command(name="show", aliases=["list", "queue"])
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
        paginator = discord.ext.menus.MenuPages(
            source=PlaylistPaginator(playlist.songs,
                                     ctx=ctx,
                                     playlist=playlist),
            clear_reactions_after=True,
        )
        await paginator.start(ctx)

    @discord.ext.commands.command(name="add")
    async def add(self, ctx: DJDiscordContext, *,
                  song: SongConverter) -> typing.Optional[discord.Message]:
        playlist = await PlaylistConverter().convert(ctx, str(ctx.author.id))
        message = ctx.bot.templates.playlistChange.copy()
        await playlist.add_song(ctx, song)
        return await ctx.send(embed=message.add_field(
            name="New Song!", value="%s {}".format(song.title) % song.emoji))

    @discord.ext.commands.command(name="create", aliases=["new"])
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
                color=0xF2E94E,
            ).add_field(name="Playlist Code", value=playlist_id)
            # .add_field(name="Song Limit", value="%d" % 40 if ctx.author.premium else 20)
            .set_thumbnail(url=response.attachments[0].url).set_image(
                url=
                "https://cdn.discordapp.com/attachments/783142801294098474/800616839754678272/congrats.gif"
            ))


def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_cog(PlaylistCommands())
