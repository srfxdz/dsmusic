import json
import os

import discord
from discord import app_commands
from discord.app_commands import AppCommandChannel
from discord.ext import commands


@app_commands.guild_only()
class Tracker(commands.Cog):
    tracking: dict[str, str] = {}

    def __init__(self, bot: discord.Client, data_file: str = "config/tracker.json"):
        self.bot = bot

        if os.path.exists(data_file) and os.path.isfile(data_file):
            with open(data_file) as f:
                self.tracking = json.load(f)

    @commands.Cog.listener("on_presence_update")
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Check if a tracked user is online"""
        if before.status != after.status and after.status == discord.Status.online:
            if str(after.id) in self.tracking:
                channel = self.bot.get_channel(int(self.tracking[str(after.id)]))
                if channel.guild == after.guild:
                    await channel.send(f"{after.mention} is now {after.status}")

    def add(self, user: discord.Member, channel: discord.TextChannel):
        self.tracking[str(user.id)] = str(channel.id)

        with open("config/tracker.json", "w") as f:
            json.dump(self.tracking, f)

    def remove(self, user: discord.Member):
        del self.tracking[str(user.id)]

        with open("config/tracker.json", "w") as f:
            json.dump(self.tracking, f)

    @app_commands.command(name="track", description="Track a user status")
    @app_commands.describe(username="The user you want to track")
    @app_commands.describe(channel="The channel you want to send the status updates to")
    async def track(self, interaction: discord.Interaction, username: discord.Member, channel: AppCommandChannel):
        """Track a user status"""
        # noinspection PyTypeChecker
        resp: discord.InteractionResponse = interaction.response

        channel = await channel.fetch()
        if isinstance(channel, discord.TextChannel):
            self.add(username, channel)
            await resp.send_message(f"👍 Tracking user {username.mention} in channel {channel.mention}")
        else:
            await resp.send_message("❌ Invalid channel", ephemeral=True)

    @app_commands.command(name="untrack", description="Untrack a user status")
    @app_commands.describe(username="The user you want to untrack")
    async def untrack(self, interaction: discord.Interaction, username: discord.Member):
        """Untrack a user status"""
        # noinspection PyTypeChecker
        resp: discord.InteractionResponse = interaction.response

        self.remove(username)
        await resp.send_message(f"👍 Untracking user {username.mention}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tracker(bot))
