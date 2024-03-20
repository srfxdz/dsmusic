import asyncio
import json
import logging
import os
from os import getenv

import discord
import mafic
from discord import app_commands
from discord.ext import commands
from mafic import NodeAlreadyConnected

__all__ = [
    "Client"
]

logger = logging.getLogger('discord.dsbot')


async def response_after_error(interaction: discord.Interaction, message: str):
    try:
        await interaction.response.send_message(message, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(message, ephemeral=True)


class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add nodes
        self.pool = mafic.NodePool(self)

        # App commands
        self.guild_id = discord.Object(id=getenv("DS_GUILD_ID", 0))
        self.tree.on_error = self.on_tree_error

    async def setup_hook(self):
        logger.info("Loading extensions")
        await self.load_extension("dsmusic.tracker.cog")
        await self.load_extension("dsmusic.assistant.cog")

        if int(os.getenv("DISABLE_LAVALINK", "0")) == 1:
            logger.warning("Lavalink is disabled")
        else:
            await self.loop.create_task(self.add_nodes())
            await self.load_extension("dsmusic.music.cog")

        logger.info("Extensions loaded")

        # This copies the global commands over to your guild.
        logger.info("Syncing command tree")
        self.tree.copy_global_to(guild=self.guild_id)
        await self.tree.sync(guild=self.guild_id)

    async def add_nodes(self):
        """Add and connect to lavalink nodes"""
        logger.info("Adding lavalink nodes")

        if os.path.exists("config/lavalink.json") and os.path.isfile("config/lavalink.json"):
            with open("config/lavalink.json") as f:
                data = json.load(f)
        elif os.path.isdir("config/lavalink.json"):
            logger.error("Lavalink config is a directory")
            return
        else:
            with open("config/lavalink.json", "w") as f:
                f.write("[]")
            logger.error("Lavalink config not available")
            return

        for node_info in data:
            try:
                async with asyncio.timeout(10):
                    await self.pool.create_node(
                        host=node_info["uri"],
                        port=node_info["port"],
                        label=f"CONFIG-{data.index(node_info)}",
                        password=node_info["password"],
                        secure=False,
                        timeout=5,
                    )
                    logger.info(f"Node {node_info['uri']} added")
            except NodeAlreadyConnected:
                pass
            except (TimeoutError, asyncio.TimeoutError):
                logger.error(f"Node {node_info['uri']} timed out")
            except RuntimeError:
                logger.error(f"Node {node_info['uri']} failed")
            except Exception as e:
                logger.error(e)
                pass

        if len(self.pool.nodes) == 0:
            logger.error("No nodes connected")
        else:
            logger.info(f"{len(self.pool.nodes)} nodes connected")

    # noinspection PyUnresolvedReferences
    @staticmethod
    async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await response_after_error(interaction, f"You are currently on cooldown!")
        elif isinstance(error, app_commands.MissingPermissions):
            return await response_after_error(
                interaction, "I don't have the required permissions to execute this command")
        else:
            logger.error(error)
            return await response_after_error(interaction, "An error occurred")
