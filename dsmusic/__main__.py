import os

import discord

from .client import Client

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()

intents = discord.Intents(131)

client = Client(
    intents=intents,
    command_prefix="!",
    max_messages=None,
    assume_unsync_clock=True,
    activity=discord.CustomActivity(name="We Live. We Love. We Lie."),
    status=discord.Status.online,
    mentions=discord.AllowedMentions.none(),
    help_command=None,
    owner_id=333947212520357889,
)

oauth_url = discord.utils.oauth_url(839827510761488404, guild=discord.Object(681419392637993013))
print(oauth_url)

token = os.getenv("TOKEN")

if token:
    client.run(token=token)
else:
    raise ValueError("Missing token")
