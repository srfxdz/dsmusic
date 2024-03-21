import os
import logging

import discord

from .client import Client

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()


def setup_discord_auxiliary_objects():
    intents = discord.Intents(
        guilds=True,
        members=True,
        messages=True,
        voice_states=True,
        presences=True,
        message_content=True
    )

    permissions = discord.Permissions(
        send_messages=True,
        read_messages=True,

        connect=True,
        speak=True,
        use_voice_activation=True,
        use_soundboard=True,

        manage_threads=True,
        send_messages_in_threads=True,

        attach_files=True,
        embed_links=True,
    )

    return intents, permissions


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.client').setLevel(logging.INFO)
    logging.getLogger('mafic').setLevel(logging.WARNING)
    logging.getLogger('mafic.strategy').setLevel(logging.CRITICAL)


def main():
    setup_logging()
    intents, permissions = setup_discord_auxiliary_objects()

    client = Client(
        intents=intents,
        command_prefix="!",
        activity=discord.CustomActivity(name="Gressinbon"),
        status=discord.Status.online,
        mentions=discord.AllowedMentions.none(),
        help_command=None
    )

    oauth_url = discord.utils.oauth_url(
        client_id=839827510761488404,
        guild=discord.Object(os.getenv("DS_GUILD_ID")),
        permissions=permissions
    )
    print(f"Bot URL: {oauth_url}")

    token = os.getenv("DS_TOKEN")

    if token:
        client.run(token=token, log_handler=None)
    else:
        raise ValueError("Missing token")


if __name__ == "__main__":
    main()
