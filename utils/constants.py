import datetime
import typing
from dataclasses import dataclass
from urllib.parse import urlparse
from __future__ import annotations # Py 3.10

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
    @staticmethod
    def debug(_):
        pass

    @staticmethod
    def warning(_):
        pass

    @staticmethod
    def error(_):
        pass

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class Evaluation:
    pass

class DatabaseEvalResults:
    OK = 0
    WARNING = 1
    ERROR = 2

@dataclass
class DatabaseConfigChange:
    new_val: typing.Optional[dict]
    old_val: typing.Optional[dict]

    @staticmethod
    def from_raw(_raw: typing.List[dict]) -> typing.Iterator[DatabaseConfigChange]:
        for change in _raw:
            yield DatabaseConfigChange(change.get("new_val"), change.get("old_val"))

@dataclass
class DatabaseEvaluation:
    config_changes: typing.Iterator[DatabaseConfigChange]
    dbs_dropped: typing.Optional[int]
    tables_dropped: typing.Optional[int]
    dbs_created: typing.Optional[int]

    @staticmethod
    def from_dict(_dict: dict) -> DatabaseEvaluation:
        dbs_dropped = None
        dbs_created = None
        tables_dropped = None

        raw_config_changes = _dict["config_changes"]

        if _dict.get("dbs_dropped") is not None:
            dbs_dropped = _dict.get("dbs_dropped")
        
        if _dict.get("dbs_created") is not None:
            dbs_created = _dict.get("dbs_created")

        if _dict.get("tables_dropped") is not None:
            tables_dropped = _dict.get("tables_dropped")

        config_changes = DatabaseConfigChange.from_raw(raw_config_changes)
            
        return DatabaseEvaluation(config_changes, dbs_dropped, tables_dropped, dbs_created)


@dataclass
class TableEvaluation:
    opcode: int
    config_changes: typing.Iterator[DatabaseConfigChange]
    
    @staticmethod
    def from_dict(_dict: dict) -> TableEvaluation:
        if _dict.get("errors"):
            opcode = DatabaseEvalResults.ERROR
        elif _dict.get("warnings"):
            opcode = DatabaseEvalResults.WARNING
        else:
            opcode = DatabaseEvalResults.OK

        raw_config_changes = _dict["config_changes"]

        config_changes = DatabaseConfigChange.from_raw(raw_config_changes)

        return TableEvaluation(opcode, config_changes)

@dataclass
class DocumentEvaluation:
    opcode: int
    errors: typing.Optional[list]
    warnings: typing.Optional[list]
    changed: int
    replaced: int
    inserted: int
    skipped: int
    unchanged: int
    deleted: int

    @staticmethod
    def from_dict(_dict: dict) -> DocumentEvaluation:
        changed = _dict.get("changed")
        replaced = _dict["replaced"]
        inserted = _dict["inserted"]
        skipped = _dict["skipped"]
        changed = _dict["changed"]
        unchanged = _dict["unchanged"]
        deleted = _dict["deleted"]

        errors = None
        warnings = None

        if _errors := _dict.get("errors"):
            opcode = DatabaseEvalResults.ERROR
            errors = _errors
        elif _warnings := _dict.get("warnings"):
            opcode = DatabaseEvalResults.WARNING
            warnings = _warnings
        else:
            opcode = DatabaseEvalResults.OK

        return DocumentEvaluation(opcode, errors, warnings, changed, replaced, inserted, skipped, unchanged, deleted)

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
