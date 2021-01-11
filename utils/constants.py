import datetime
import typing
from dataclasses import dataclass
from urllib.parse import urlparse

import discord.ext.commands
import rethinkdb

song_emoji_conversion = {
    "open.spotify.com": "<:spotify:790187623569424424>",
    "soundcloud.com": "<:soundcloud:790187780486987796>",
    "www.youtube.com": "<:youtube:790189633727627294>",
}


class Template(type):
    """Template type"""


class Templates(metaclass=Template):
    eval = discord.Embed(title="Evaluation Complete!",
                         description="Evaluations are closely monitored for data leaks and as such this message "
                                     "will self destruct in 10 seconds", color=4128651)

    incompleteCmd = discord.Embed(title="**`ERROR`** - Insufficent Arguments",
                                  description="Or in layman's terms, you need to give a bit more for this to work\n```\nUsage:\n{0.bot.command_prefix}{0.command.name} <command> <arguments>\n```")
    cmdError = discord.Embed(title="**`ERROR`** - Internal Error",
                             description="Or in layman's terms, you may need to tell the developers about this\n```\n{}```").set_image(
        url="https://media4.giphy.com/media/TqiwHbFBaZ4ti/giphy.gif")
    playlistChange = discord.Embed(title="Done!", description="Feel free to share this playlist with your friends!",
                                   color=0x3EFF8B)
    playlistPaginator = discord.Embed(title="Songs in **`{}`**'s playlist'", description="Playlist ID: {}",
                                      color=0xE9B44C)
    playlistsPaginator = discord.Embed(title="Songs for `{}`", description="Total: {} playlists", color=0xF2DDA4)


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


class YoutubeLogger(object):
    def debug(self, _):
        pass

    def warning(self, _):
        pass

    def error(self, _):
        pass

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# class RethinkDBEvaluationResult(discord.Enum):
#     OK = 0
#     WARNING = 1
#     ERROR = 2

@dataclass
class Playlist:
    id: int
    songs: list
    author: typing.Union[discord.Member, int, discord.User]
    cover: str

    async def delete_at(self, ctx: discord.ext.commands.Context, index: int):
        await rethinkdb.r.table("accounts").get(self.id).update(
            {"songs": rethinkdb.r.row["songs"].delete_at(index - 1)}).run(ctx.database.rdbconn)

    async def add_song(self, ctx: discord.ext.commands.Context, song: Song) -> None:
        await rethinkdb.r.table("accounts").get(self.id).update(
            {"songs": rethinkdb.r.row["songs"].append(song.json)}
        ).run(ctx.database.rdbconn)
