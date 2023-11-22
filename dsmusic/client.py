import asyncio
import json
import logging
import os
from os import getenv

import discord
import mafic
from mafic import NodeAlreadyConnected
from discord import app_commands
from discord.ext import commands

__all__ = [
    "Client"
]


logger = logging.getLogger('discord.dsbot')


class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add nodes
        self.pool = mafic.NodePool(self)

        # App commands
        self.guild_id = discord.Object(id=getenv("GUILD_ID", 0))
        self.tree.on_error = self.on_tree_error

    async def setup_hook(self):
        await self.load_extension("dsmusic.tracker.cog")
        # Add lavalink nodes
        await self.add_nodes()

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
                node = await self.pool.create_node(
                    host=node_info["uri"],
                    port=node_info["port"],
                    label=f"CONFIG-{data.index(node_info)}",
                    password=node_info["password"],
                    secure=False,
                    timeout=5,
                )
                await node.connect()
                logger.info(f"Node {node_info['uri']} added")
            except NodeAlreadyConnected:
                pass
            except TimeoutError:
                logger.error(f"Node {node_info['uri']} timed out")
            except RuntimeError:
                logger.error(f"Node {node_info['uri']} failed")
            except Exception as e:
                logger.error(e)
                pass

        if len(self.pool.nodes) == 0:
            logger.error("No nodes connected")
            return

        # Load extensions
        await self.load_extension("dsmusic.music.cog")

    # noinspection PyUnresolvedReferences
    @staticmethod
    async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await interaction.response.send_message(
                f"You are currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message(f"You are not authorized to use that", ephemeral=True)
        else:
            logger.error(error)
