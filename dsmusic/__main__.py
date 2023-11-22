import os

import discord

from .client import Client

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()

intents = discord.Intents(387)

client = Client(
    intents=intents,
    command_prefix="!",
    max_messages=None,
    assume_unsync_clock=False,
    activity=discord.CustomActivity(name="Get Joshed."),
    status=discord.Status.online,
    mentions=discord.AllowedMentions.none(),
    help_command=None
)

oauth_url = discord.utils.oauth_url(839827510761488404, guild=discord.Object(os.getenv("GUILD_ID")))
print(f"Bot URL: {oauth_url}")

token = os.getenv("TOKEN")

if token:
    client.run(token=token)
else:
    raise ValueError("Missing token")
