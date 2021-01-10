import datetime
import re
import textwrap
import typing
from urllib.parse import urlparse

import discord
import discord.ext.commands
import discord.ext.menus
import rethinkdb
import youtube_dl
import discord_argparse

from utils.constants import ydl_opts
from utils.constants import Playlist
from utils.constants import Song
from utils.constants import song_emoji_conversion

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
    async def convert(self, ctx: discord.ext.commands.Context, argument: str):
        try:
            argument = int(argument)
        except ValueError:
            return

        if argument <= 0:
            return

        return argument


class VolumeConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: discord.ext.commands.Context, argument: str):
        try:
            argument = int(argument)
        except ValueError:
            return

        if argument <= 0 or argument > 100:
            return

        return argument


class PlaylistConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: discord.ext.commands.Context,
                      argument: str) -> Playlist:
        try:
            author = await discord.ext.commands.MemberConverter().convert(
                ctx, argument)
            playlist = (await ctx.database.get(author=author.id))[0]
            return Playlist(playlist["id"], playlist["songs"],
                            playlist["author"], playlist["cover"])
        except Exception as exc:
            if isinstance(exc, discord.ext.commands.MemberNotFound):
                pass
            if isinstance(exc, IndexError):
                return

        if (re.compile(
                "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
        ).match(argument) is not None):
            playlist = (
                await
                rethinkdb.r.db("djdiscord").table("accounts").get(argument).run(
                    ctx.database.rdbconn))
            return Playlist(playlist["id"], playlist["songs"],
                            playlist["author"], playlist["cover"])

        slot = (await ctx.database.get(name=argument))[0]
        return Playlist(slot["id"], slot["songs"], playlist["author"],
                        playlist["cover"])


class SongConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: discord.ext.commands.Context,
                      argument: str) -> Song:
        target = "ytsearch:%s" % argument

        if urlparse(argument).netloc in (
                "open.spotify.com",
                "www.youtube.com",
                "soundcloud.com",
        ):
            target = argument

        with youtube_dl.YoutubeDL(ydl_opts) as ytdl:
            if data := ytdl.extract_info(target, download=False):
                if "entries" in data:
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
                 ctx: discord.ext.commands.Context,
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
        if not page:
            template.add_field(
                name="Take this lemon \U0001f34b",
                value="You have no songs in your playlist, go add some!")

        for index, song in enumerate(page, start=offset):
            template.add_field(
                name="%s `{}.` {}".format(index + 1, song["title"]) %
                song_emoji_conversion[urlparse(song["url"]).netloc],
                value=
                "Created: `{0[created]}`\nDuration: `{0[length]}` seconds, Author: `{0[uploader]}`"
                .format(song),
                inline=False)

        return template


class NameValidator(discord.ext.commands.Converter):
    async def convert(
        self: discord.ext.commands.Converter,
        _: discord.ext.commands.Context,
        argument: str,
    ):
        # if ctx.author.premium:
        # return textwrap.shorten(argument, 40)
        return textwrap.shorten(argument, 20)


class PlaylistsPaginator(discord.ext.menus.ListPageSource):
    def __init__(self, *, ctx: discord.ext.commands.Context,
                 playlists: typing.List[dict]):
        super().__init__(playlists, per_page=1)
        self.author = ctx.author
        self.templates = ctx.bot.templates
        self.playlists = playlists

    async def format_page(self, menu, page):
        format = self.templates.playlistsPaginator.copy()
        format.title = format.title.format(self.author.name)
        format.description = format.description.format(len(self.playlists))
        format.add_field(name="`%s`" % page["name"],
                         value="ID: `{0[id]}`, Song Count: `{1}`".format(
                             page, len(page["songs"])))
        return format
