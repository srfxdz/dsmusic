import logging
from random import randint
from typing import Optional

import discord
from mafic import Track, Playlist

__all__ = [
    "Queue"
]


logger = logging.getLogger('dsbot.music.queue')


def playlist_embed(result: Playlist) -> discord.Embed:
    if result.tracks[0].source == "youtube":
        color = discord.Color.red()
    elif result.tracks[0].source == "soundcloud":
        color = discord.Color.orange()
    else:
        color = discord.Color.random()

    embed = discord.Embed(color=color)

    embed.title = result.name
    embed.description = "Playlist"
    embed.set_thumbnail(url=result.tracks[0].artwork_url)

    return embed


def track_embed(result: Track) -> discord.Embed:
    if result.source == "twitch":
        color = discord.Color.purple()
    elif result.source == "youtube":
        color = discord.Color.red()
    elif result.source == "soundcloud":
        color = discord.Color.orange()
    else:
        color = discord.Color.random()

    embed = discord.Embed(color=color)

    embed.title = result.title
    embed.url = result.uri
    embed.set_author(name=result.author)
    embed.set_thumbnail(url=result.artwork_url)

    if not result.stream:
        embed.add_field(name="Video duration", value=parse_seconds(result.length // 1000))
    else:
        embed.add_field(name="Live on", value=result.source)

    return embed


def parse_seconds(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    result = "%(minutes)02d:%(seconds)02d" % {"minutes": minutes, "seconds": seconds}

    if hours != 0:
        result = f"{hours}:" + result
    return result


class Queue:
    _current: Track | None = None
    _queue: list[Track] = []
    _queue_length: int = 0

    _loop_queue: bool = False
    _loop_current: bool = False
    _shuffle: bool = False

    def toggle_loop(self, status: Optional[bool] = None) -> bool:
        """
        Loop the current queue
        :param status: force a certain status on the loop queue
        :return: the current status
        """
        if status:
            self._loop_queue = status
        else:
            self._loop_queue = not self._loop_queue

        return self._loop_queue

    def toggle_repeat(self, status: Optional[bool] = None) -> bool:
        """
        Repeat the current song
        :param status: force a certain status on the repeat value
        :return: the current status
        """
        if status:
            self._loop_current = status
        else:
            self._loop_current = not self._loop_current

        return self._loop_current

    def toggle_shuffle(self, status: Optional[bool] = None) -> bool:
        """
        Play the queue in a random order
        :param status: force a certain status on the shuffle value
        :return: the current status
        """
        if status:
            self._shuffle = status
        else:
            self._shuffle = not self._shuffle

        return self._shuffle

    def _add_to_queue(self, track: Track) -> int:
        """
        Add a track to the queue
        :param track: the track to add
        :return: if the track was added
        """
        track_length = track.length // 1000

        if track_length > 3600:  # max 1 hour
            return -2
        elif self._queue_length + track_length >= 8200:  # total max 132 minutes
            return -1
        elif len(self._queue) > 48:  # max 48 songs
            return 0
        else:
            self._queue_length += track_length
            self._queue.append(track)
            return 1

    def add(self, data: Playlist | Track | list) -> discord.Embed | None:
        """
        Add a playlist or a single track to the queue

        :param data: A playlist or a single track
        :return: an Embed for the added object or None if the object was not added
        """
        if isinstance(data, Track):
            if self._add_to_queue(track=data) == 1:
                embed = track_embed(data)
            else:
                return None
        elif isinstance(data, Playlist):
            added = 0
            for track in data.tracks:
                ret = self._add_to_queue(track=track)
                if ret == 1:
                    added += 1
                elif ret == 0:
                    break
            embed = playlist_embed(data).add_field(name="Number of videos", value=added)
        elif isinstance(data, list):
            if len(data) == 0:
                return None
            return self.add(data[0])
        else:
            return None

        return embed

    def next(self) -> Track | None:
        """
        Get the next track to play
        :return: a Track object
        """
        if len(self._queue) == 0:
            self._current = None
            return None

        if self._loop_current:
            return self._current

        if self._shuffle:
            index = randint(0, len(self._queue)) % len(self._queue)
        else:
            index = 0

        try:
            track = self._queue.pop(index)
        except IndexError:
            logger.error(f"IndexError in Queue.next, queue length: {len(self._queue)}, index: {index}")
            self._current = None
            return None

        if self._loop_queue:
            self._queue.append(track)
        else:
            self._queue_length -= track.length

        self._current = track
        return track

    def clean(self) -> int:
        """
        Reset the queue removing all the elements
        :return: the number of elements removed
        """
        size = len(self._queue)
        del self._queue
        self._queue = []
        self._queue_length = 0
        self._current = None

        return size
