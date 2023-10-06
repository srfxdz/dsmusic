from typing import Generic

import mafic
# noinspection PyProtectedMember
from discord._types import ClientT

from .queue import Queue


class LavalinkPlayer(mafic.Player, Generic[ClientT]):
    queue: Queue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = Queue()

    def clean_queue(self):
        """
        Delete queue
        :return: None
        """
        del self.queue
        self.queue = Queue()
