import datetime
import re
import textwrap
import typing
from urllib.parse import urlparse
from utils.exceptions import OutOfBoundVolumeError, VolumeTypeError, PlaylistGivenError

import dateutil.relativedelta
import discord
import discord.ext.commands
import discord.ext.menus
import discord_argparse
import rethinkdb
import youtube_dl

from utils.objects import Playlist
from utils.objects import Song
from utils.objects import Station
from utils.objects import song_emoji_conversion
from utils.objects import ydl_opts
from utils.extensions import DJDiscordContext

ArgumentConverter = discord_argparse.ArgumentConverter(
    dj_role=discord_argparse.OptionalArgument(
        discord.Role,
        doc="DJ Role ID that controls voice channel operations.",
        default=None),
    announcement=discord_argparse.OptionalArgument(
        discord.TextChannel,
        doc="Announcement channel ID for DJ Discord announcments",
        default=None))


class IndexConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: DJDiscordContext, argument: str):
        try:
            argument = int(argument)
        except ValueError:
            return

        if argument <= 0:
            return

        return argument


class VolumeConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: DJDiscordContext, argument: str):
        if not argument.isdigit() and not isinstance(argument, int):
            raise VolumeTypeError(int, type(argument))

        if int(argument) < 0 or int(argument) > 200:
            raise OutOfBoundVolumeError(
                "The given volume exceeds the boundary of Lavalink and Discord.py"
            )

        return int(argument)


class StationConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: DJDiscordContext,
                      argument: str) -> typing.Optional[Station]:
        if len(argument) == 4 and re.compile(
                r"[AKNWaknw][a-zA-Z]{0,2}[0123456789][a-zA-Z]{1,3}").match(
                    argument):
            raw = await ctx.database.get(call_sign=argument, table="stations")
            return Station.from_json(raw)

        if re.compile(r'^-?\d+(?:\.\d+)$').match(
                argument) and 87.5 <= float(argument) <= 108:
            if raw := await ctx.database.get(frequency=float(argument),
                                             table="stations"):
                return Station.from_json(raw[0])


class PlaylistConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: DJDiscordContext, argument: str) -> Playlist:
        try:
            author = await discord.ext.commands.MemberConverter().convert(
                ctx, argument)
            playlist = (await ctx.database.get(author=author.id))[0]
            return Playlist.from_json(playlist)
        except Exception as exc:
            if isinstance(exc,
                          discord.ext.commands.MemberNotFound) or isinstance(
                              exc, IndexError):
                return

        if (re.compile(
                "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
        ).match(argument) is not None):
            playlist = (await ctx.database.run(
                rethinkdb.r.table("playlists").get(argument)))
            return Playlist(playlist["id"], playlist["songs"],
                            playlist["author"], playlist["cover"])

        slot = (await ctx.database.get(name=argument))[0]
        return Playlist(slot["id"], slot["songs"], slot["author"],
                        slot["cover"])


class SongConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: DJDiscordContext, argument: str) -> Song:
        target = "ytsearch:%s" % argument

        if urlparse(argument).netloc in ("www.youtube.com", "soundcloud.com",
                                         "www.twitch.tv"):
            target = argument
        elif urlparse(argument).netloc == "open.spotify.com":
            playlist_regex = re.compile(
                r"^(https:\/\/open.spotify.com\/playlist\/)([a-zA-Z0-9]+)(.*?)"
            )
            song_regex = re.compile(
                r"^(https:\/\/open.spotify.com\/track\/)([a-zA-Z0-9]+)(.*?)")
            if playlist_regex.match(argument) is not None:
                raise PlaylistGivenError
            elif song_regex.match(argument) is not None:
                track = await ctx.spotify.track.get_one(
                    argument.split("track/")[-1])
                with youtube_dl.YoutubeDL(ydl_opts) as ytdl:
                    if data := ytdl.extract_info("ytsearch:%s" % track["name"],
                                                 download=False):
                        print(data)
                        return Song(
                            data["entries"][0]["formats"][0]["url"],
                            data["entries"][0]["webpage_url"],
                            ", ".join(artist["name"]
                                      for artist in track["artists"]),
                            track["name"], data["entries"][0]["thumbnails"],
                            datetime.datetime.strptime(
                                data["entries"][0]["upload_date"],
                                "%Y%m%d").astimezone().strftime("%Y-%m-%d"),
                            track["duration_ms"])

        with youtube_dl.YoutubeDL(ydl_opts) as ytdl:
            if data := ytdl.extract_info(target, download=False):
                if "entries" in data and data.get("entries"):
                    return Song(
                        data["entries"][0]["formats"][0]["url"],
                        data["entries"][0]["webpage_url"],
                        data["entries"][0]["uploader"],
                        data["entries"][0]["title"],
                        data["entries"][0]["thumbnails"],
                        datetime.datetime.strptime(
                            data["entries"][0]["upload_date"],
                            "%Y%m%d").astimezone().strftime("%Y-%m-%d"),
                        data["entries"][0]["duration"])

                return Song(
                    data["formats"][0]["url"],
                    data["webpage_url"],
                    data["uploader"],
                    data["title"],
                    data["thumbnails"],
                    datetime.datetime.strptime(
                        data["upload_date"],
                        "%Y%m%d").astimezone().strftime("%Y-%m-%d"),
                    data["duration"],
                )

            return None


class PlaylistPaginator(discord.ext.menus.ListPageSource):
    def __init__(self,
                 entries: typing.List[str],
                 *,
                 playlist: Playlist,
                 ctx: DJDiscordContext,
                 per_page: int = 4):
        super().__init__(entries, per_page=per_page)
        self.templates = ctx.bot.templates
        self.playlist = playlist
        self.author = ctx.author

    async def format_page(self, menu, page: typing.List[str]) -> discord.Embed:
        offset = menu.current_page * self.per_page

        template = self.templates.playlistPaginator.copy()
        template.title = template.title.format(str(self.author))
        template.description = template.description.format(self.playlist.id)

        if self.playlist.cover:
            template.set_thumbnail(url=self.playlist.cover)

        if not page:
            template.add_field(
                name="Take this lemon \U0001f34b",
                value="You have no songs in your playlist, go add some!")

        for index, song in enumerate(page, start=offset):
            template.add_field(
                name="%s `{}.` {}".format(index + 1, song["title"]) %
                song_emoji_conversion[urlparse(song["url"]).netloc],
                value="Created: `{0[created]}`\n"
                "Duration: `{0[length]}` seconds, Author: `{0[uploader]}`".
                format(song),
                inline=False)

        return template


class TrackPositionConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: discord.ext.commands.Context,
                      argument: str) -> float:
        regex = re.compile(r"(?:(?P<years>\d)y)?"
                           r"(?:(?P<months>\d{1,2})mo)?"
                           r"(?:(?P<weeks>\d{1,4})w)?"
                           r"(?:(?P<days>\d{1,5})d)?"
                           r"(?:(?P<hours>\d{1,5})h)?"
                           r"(?:(?P<minutes>\d{1,5})m)?"
                           r"(?:(?P<seconds>\d{1,5})s)?")
        if "%" in argument:
            return ctx.player.position * (float(argument.strip("%")) / 100)
        if match := regex.fullmatch(argument):
            duration_dict = {
                k: int(v)
                for k, v in match.groupdict(default=0).items()
            }
            delta: datetime.datetime = datetime.datetime.now(
            ) + dateutil.relativedelta.relativedelta(**duration_dict)
            return (delta.timestamp() -
                    datetime.datetime.now().timestamp()) * 1000
        try:
            if float(argument) >= 1000.0:
                return float(argument)
        except ValueError:
            return


class NameValidator(discord.ext.commands.Converter):
    async def convert(
        self: discord.ext.commands.Converter,
        _: DJDiscordContext,
        argument: str,
    ):
        # if ctx.author.premium:
        # return textwrap.shorten(argument, 40)
        return textwrap.shorten(argument, 20)


class VoicePrompt(discord.ext.menus.Menu):
    def __init__(self, message: str) -> None:
        super().__init__(timeout=5.0, delete_message_after=True)
        self.msg = message
        self.voted = 0

    async def send_initial_message(self, ctx, channel):
        return await channel.send(self.msg)

    @discord.ext.menus.button("👍")
    async def vote_inc(self, payload) -> None:
        self.voted += 1

    @discord.ext.menus.button("👎")
    async def vote_dec(self, payload) -> None:
        self.voted -= 1

    async def prompt(self, ctx: DJDiscordContext) -> None:
        await self.start(ctx, wait=True)
        return self.voted


class PlaylistsPaginator(discord.ext.menus.ListPageSource):
    def __init__(self, *, ctx: DJDiscordContext, playlists: typing.List[dict]):
        super().__init__(playlists, per_page=1)
        self.author = ctx.author
        self.templates = ctx.bot.templates
        self.playlists = playlists

    async def format_page(self, menu, page):
        embed = self.templates.playlistsPaginator.copy()
        embed.title = embed.title.format(self.author.name)
        embed.description = format.description.format(len(self.playlists))
        embed.add_field(embed="`%s`" % page["name"],
                        value="ID: `{0[id]}`, Song Count: `{1}`".format(
                            page, len(page["songs"])))
        return embed
