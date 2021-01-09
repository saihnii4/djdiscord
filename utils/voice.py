import asyncio
from ssl import get_protocol_name
import discord.ext.commands

from utils.constants import Playlist


class VoiceError(Exception):
    pass


class VoiceState:
    def __init__(self, bot: discord.ext.commands.Bot,
                 ctx: discord.ext.commands.Context, playlist: Playlist):
        self.bot = bot
        self._ctx = ctx
        self.playlist = playlist

        self.song_iter = iter(self.playlist.songs)
        self.current = next(self.song_iter)
        self.voice = None
        self.next = next(self.song_iter)

        self._loop = False
        self.skip_votes = set()

    def __del__(self):
        self.song_iter = None
        self.current = None
        self.voice = None
        self.next = None

        del self._ctx.voice_queue[self._ctx.guild.id]

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def is_playing(self):
        return self.voice and self.current

    def shift(self) -> None:
        if self._loop:
            self.next = self.current
            return

        self.current = self.next

        try:
            self.next = next(self.song_iter)
        except StopIteration:
            self.next = None

    def skip(self):
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.song_iter = None
        self.current = None
        self.next = None

        if self.voice:
            await self.voice.disconnect()
            self.voice = None
