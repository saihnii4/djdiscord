import datetime
import re
import time
import typing
import uuid
import youtube_dl
import textwrap
import rethinkdb
from urllib.parse import urlparse
from dataclasses import dataclass
import discord.ext.commands
import discord.ext.menus
import discord

song_emoji_conversion = {
    "open.spotify.com": "<:spotify:790187623569424424>",
    "soundcloud.com": "<:soundcloud:790187780486987796>",
    "www.youtube.com": "<:youtube:790189633727627294>",
}


class PlaylistPaginator(discord.ext.menus.ListPageSource):
    def __init__(self, entries: typing.List[str], *, ctx: discord.ext.commands.Context, per_page: int = 4):
        super().__init__(entries, per_page=per_page)
        self.templates = ctx.templates

    async def format_page(self, menu, page: typing.List[str]) -> discord.Embed:
        offset = menu.current_page * self.per_page
        format = self.templates.playlistPaginator.copy()
        for song in page:
            format.add_field(name="%s {}".format(song.title) % song_emoji_conversion[urlparse(song.url).netloc],
                             value="Created: `{0.created}`\nDuration: `{0.length}` seconds, Author: `{0.uploader}`".format(song),
                             inline=False)
        return format

@dataclass
class Song:
    source: str
    url: str
    uploader: str
    title: str
    thumbnails: typing.Union[list, str]
    created: typing.Union[datetime.datetime, str]
    length: typing.Union[str, int, datetime.datetime]
    # lyrics: typing.Union[str, SongLyrics]

    @property
    def emoji(self) -> str:
        return song_emoji_conversion[urlparse(self.url).netloc]

    @property
    def json(self) -> dict:
        return {
            "source": self.source,
            "uploader": self.uploader,
            "title": self.title,
            "thumbnails": self.thumbnails,
            "created": self.created,
            "length": self.length,
            "url": self.url,
        }



@dataclass
class Playlist:
    id: str
    name: str
    songs: list
    author: typing.Union[discord.Member, int, discord.User]

    async def add_song(self, ctx: discord.ext.commands.Context, song: Song) -> None:
        await ctx.database.database.table("accounts").get(self.id).update(
            {"songs": rethinkdb.r.row["songs"].append(song.json)}
        ).run(ctx.database.connection)


class NameValidator(discord.ext.commands.Converter):
    async def convert(
        self: discord.ext.commands.Converter,
        _: discord.ext.commands.Context,
        argument: str,
    ):
        # if ctx.author.premium:
        # return textwrap.shorten(argument, 40)
        return textwrap.shorten(argument, 20)

class PlaylistPaginator(discord.ext.menus.ListPageSource):
    def __init__(self, entries: typing.List[dict], *, ctx: discord.ext.commands.Context, playlist: Playlist, per_page: int = 4):
        super().__init__(entries, per_page=per_page)
        self.templates = ctx.bot.templates
        self.playlist = playlist

    async def format_page(self, menu, page: typing.List[dict]) -> discord.Embed:
        offset = menu.current_page * self.per_page
        format = self.templates.playlistPaginator.copy()
        format.title = format.title.format(self.playlist.name)
        format.description = format.description.format(self.playlist.id)
        for song in page:
            format.add_field(name="%s {}".format(song["title"]) % song_emoji_conversion[urlparse(song["url"]).netloc],
                             value="Created: {0[created]}, Duration: {0[length]}, Author: {0[uploader]}".format(song))
        return format

class PlaylistsPaginator(discord.ext.menus.ListPageSource):
    def __init__(self, *, ctx: discord.ext.commands.Context, playlists: typing.List[dict]):
        super().__init__(playlists, per_page=1)
        self.author = ctx.author
        self.templates =  ctx.bot.templates
        self.playlists = playlists

    async def format_page(self, menu, page):
        format = self.templates.playlistsPaginator.copy()
        format.title = format.title.format(self.author.name)
        format.description = format.description.format(len(self.playlists))
        format.add_field(name="`%s`" % page["name"], value="ID: `{0[id]}`, Song Count: `{1}`".format(
            page, len(page["songs"])))
        return format


@discord.ext.commands.group(name="playlist")
async def playlist(ctx: discord.ext.commands.Context) -> None:
    if ctx.invoked_subcommand is None:
        notif = (
            ctx.bot.templates.incompleteCmd.copy()
            .set_thumbnail(url="https://media4.giphy.com/media/TqiwHbFBaZ4ti/giphy.gif")
            .set_author(
                name=ctx.author.name, icon_url=ctx.author.avatar_url_as(format="png")
            )
            .set_footer(text="Unix Time: %d" % time.time())
        )
        notif.description = notif.description.format(ctx)
        return await ctx.send(embed=notif)

@playlist.command(name="delete")
async def delete(ctx: discord.ext.commands.Context) -> None:
    return await ctx.send("NotImplementedError: This command has not been implemented yet :p")

class PlaylistConverter(discord.ext.commands.Converter):
    async def convert(self, ctx, argument):
        if (
            re.compile(
                "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
            ).match(argument)
            is not None
        ):
            playlist = (
                await ctx.database.database.table("accounts")
                .get(argument)
                .run(ctx.database.connection)
            )
            return Playlist(
                playlist["id"], playlist["name"], playlist["songs"], playlist["author"]
            )

        slot = (await ctx.database.get(ctx, name=argument))[0]
        return Playlist(slot["id"], slot["name"], slot["songs"], slot["author"])


class SongConverter(discord.ext.commands.Converter):
    async def convert(self, ctx: discord.ext.commands.Context, argument: str) -> Song:
        target = "ytsearch:%s" % argument

        if urlparse(argument).netloc in (
            "open.spotify.com",
            "www.youtube.com",
            "soundcloud.com",
        ):
            target = argument

        with youtube_dl.YoutubeDL() as ytdl:
            if data := ytdl.extract_info(target, download=False):
                if "entries" in data:
                    return Song(
                        data["entries"][0]["formats"][0]["url"],
                        data["entries"][0]["webpage_url"],
                        data["entries"][0]["uploader"],
                        data["entries"][0]["title"],
                        data["entries"][0]["thumbnails"],
                        datetime.datetime.strptime(data["entries"][0]["upload_date"], "%Y%m%d").astimezone().strftime("%Y-%m-%d"),
                        data["entries"][0]["duration"],
                    )

                return Song(
                    data["formats"][0]["url"],
                    data["webpage_url"],
                    data["uploader"],
                    data["title"],
                    data["thumbnails"],
                    datetime.datetime.strptime(data["upload_date"], "%Y%m%d").astimezone().strftime("%Y-%m-%d"),
                    data["duration"],
                )


@playlist.command(name="list")
async def list(
    ctx: discord.ext.commands.Context, playlist: PlaylistConverter = None
) -> None:
    if playlist is None:
        playlists = [entry async for entry in await ctx.database.database.table("accounts").filter({"author": ctx.author.id}).run(ctx.database.connection)]
        paginator = discord.ext.menus.MenuPages(source=PlaylistsPaginator(ctx=ctx, playlists=playlists), clear_reactions_after=True)
        return await paginator.start(ctx)
    paginator = discord.ext.menus.MenuPages(source=PlaylistPaginator(
        playlist.songs, ctx=ctx, playlist=playlist), clear_reactions_after=True)
    await paginator.start(ctx)

@playlist.command(name="add")
async def add(
    ctx: discord.ext.commands.Context, playlist: PlaylistConverter, song: SongConverter
) -> None:
    message = ctx.bot.templates.playlistChange.copy()
    await playlist.add_song(ctx, song)
    return await ctx.send(
        embed=message.add_field(
            name="New Song!", value="%s {}".format(song.title) % song.emoji
        )
    )


@playlist.command(name="create")
async def create(ctx: discord.ext.commands.Context, *, playlist: NameValidator) -> None:
    playlist_id = str(uuid.uuid4())
    await ctx.database.database.table("accounts").insert(
        {
            "name": playlist,
            "id": playlist_id,
            "author": ctx.author.id,
            "songs": [],
            "cover": None,
        }
    ).run(ctx.database.connection)

    msg = await ctx.send(
        embed=discord.Embed(title="Almost there!", color=0xDA3E52).add_field(
            name="Cover Art",
            value="Now upload your cover art, if you don't want to upload anything, ignore this message for 10 seconds",
        ).set_image(url="https://res.cloudinary.com/practicaldev/image/fetch/s--0TbCN_Xq--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_66%2Cw_880/https://dev-to-uploads.s3.amazonaws.com/i/tb6tb1wvi7f00eqns3g0.gif"
    ))

    response = await ctx.wait_for(
        "message", check=lambda message: message.author == ctx.author, timeout=10
    )

    if response is None:
        return

    if not response.attachments:
        return await ctx.send(
            "You didn't send an attachment to set as your cover art, so we stopped listening"
        )

    await ctx.database.database.table("accounts").filter({"id": playlist_id}).update(
        {"cover": response.attachments[0].url}
    ).run(ctx.database.connection)

    playlist = (
        await ctx.database
        .get(ctx,id=playlist_id)
    )[0]

    return await msg.edit(
        embed=discord.Embed(
            title="All done!",
            description="Everything is clear! Begin adding songs to your playlist!",
            color=0xF2E94E)
        .add_field(name="Playlist Code", value=playlist_id)
        # .add_field(name="Song Limit", value="%d" % 40 if ctx.author.premium else 20)
        .set_thumbnail(url=response.attachments[0].url)
        .set_image(url="https://i.pinimg.com/originals/b9/88/b7/b988b7c3e84e1f83ef9447157831b460.gif"))

def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_command(playlist)
