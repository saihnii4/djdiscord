import discord.ext.commands

from utils.objects import Playlist, Station


class VoiceError(Exception):
    pass


class VoiceState:
    def __init__(self, bot: discord.ext.commands.Bot,
                 ctx: discord.ext.commands.Context, iterator):
        self.bot = bot
        self._ctx = ctx
        self.playlist = None
        self.station = None
        self.song_iter = None
        self.current = None

        if isinstance(iterator, Station):
            self.station = iterator
            self.current = self.station
        else:
            self.playlist = iterator
            self.song_iter = iter(self.playlist.songs)
            self.current = next(self.song_iter)

        self.voice = None

        try:
            self.next = next(self.song_iter)
        except Exception as error:
            if isinstance(error, (StopIteration, TypeError)):
                self.next = None
            else:
                raise

        self._loop = False
        self.skip_votes = set()

    def __del__(self):
        self.song_iter = None
        self.current = None
        self.voice = None
        self.next = None

        if self._ctx.guild.id in self._ctx.voice_queue:
            del self._ctx.voice_queue[self._ctx.guild.id]

    @property
    def loop(self):
        if self.playlist is None:
            raise NotImplementedError(
                "voice state does not have a playlist attribute to loop")

        return self._loop

    @loop.setter
    def loop(self, value: bool):
        if self.playlist is None:
            raise NotImplementedError(
                "voice state does not have a playlist attribute to loop")
        self._loop = value

    @property
    def is_playing(self):
        return self.voice and self.current

    def shift(self) -> None:
        if self.playlist is None:
            raise NotImplementedError(
                "voice state does not have a playlist attribute to loop")

        if self._loop:
            self.next = self.current
            return

        self.current = self.next

        try:
            self.next = next(self.song_iter)
        except StopIteration:
            self.next = None

    def skip(self):
        if self.playlist is None:
            raise NotImplementedError(
                "voice state does not have a playlist attribute to loop")

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        if self.voice:
            await self.voice.disconnect()
            del self
