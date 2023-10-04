from typing import Optional

import discord
from random import randint
from mafic import Track, Playlist

__all__ = [
    "Queue"
]


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
            self._loop_current = status
        else:
            self._loop_current = not self._loop_current

        return self._loop_current

    def _add_to_queue(self, track: Track) -> int:
        """
        Add a track to the queue
        :param track: the track to add
        :return: if the track was added
        """
        track_length = track.length // 1000

        if track_length > 3600:
            return -2
        elif self._queue_length + track_length >= 7200:
            return -1
        elif len(self._queue) > 36:
            return 0
        else:
            self._queue_length += track_length
            self._queue.append(track)
            return 1

    def add(self, data: Playlist | Track | list) -> discord.Embed | None:
        """
        Add a playlist or a single track to the queue

        :param data: A playlist or a single track
        :return: an Embed for the added object
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
            return None

        if self._loop_current:
            return self._queue[0]

        if self._shuffle:
            index = randint(0, len(self._queue))
        else:
            index = 0

        track = self._queue.pop(index)

        if self._loop_current:
            self._queue.append(track)
        else:
            self._queue_length -= track.length

        return track
