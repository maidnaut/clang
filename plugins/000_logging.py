import discord, time
from inc.db import *
from inc.utils import *
from datetime import datetime
from discord.ext import commands
from discord import CategoryChannel
from collections import defaultdict, deque




def setup(bot):
    bot.add_cog(LoggingCog(bot))




class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_deletions = defaultdict(lambda: deque(maxlen=10))

    # Join log
    @commands.Cog.listener()
    async def on_member_join(self, member):

        # Drop out if in dm's
        if not member.guild:
            return

        channel = await get_channel(int(member.guild.id), "joinlog")

        if channel is not None:
            embed = discord.Embed(
                title="🎉 Member Joined",
                color=discord.Color.green(),
            )

            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.add_field(name="", value=f"{member.mention} {member.name}", inline=True)

            await channel.send(embed=embed, silent=True)

    # Leave log
    @commands.Cog.listener()
    async def on_member_remove(self, member):

        # Drop out if in dm's
        if not member.guild:
            return

        channel = await get_channel(int(member.guild.id), "joinlog")

        if channel is not None:
            embed = discord.Embed(
                title="👋 Member Left",
                color=discord.Color.red(),
            )

            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.add_field(name="", value=f"{member.mention} {member.name}", inline=True)

            await channel.send(embed=embed, silent=True)

    # on edit
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author.bot or before.content == after.content:
            return

        # Get mod category and log channel
        mod_category = await get_channel(before.guild.id, "mod_category")
        log_channel = await get_channel(int(before.guild.id), "logs")

        # Skip if log channel doesn't exist
        if not log_channel:
            return

        # Skip if message is in mod category
        if mod_category and isinstance(mod_category, discord.CategoryChannel):
            if before.channel.category_id == mod_category.id:
                return

        # Proceed with logging
        embed = discord.Embed(
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=before.author.avatar.url if before.author.avatar else None)
        embed.add_field(name="", value=f" {before.author.mention} edited a message in {before.channel.mention}", inline=False)
        embed.add_field(name="", value=f"**Message Link:** [Jump to Message]({before.jump_url})", inline=False)
        embed.add_field(name="Before", value=before.content[:1024], inline=False)
        embed.add_field(name="After", value=after.content[:1024], inline=False)
        await log_channel.send(embed=embed, silent=True)

    # on delete
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return

        # Get mod category and log channel
        mod_category = await get_channel(message.guild.id, "mod_category")
        log_channel = await get_channel(int(message.guild.id), "logs")

        # Skip if log channel doesn't exist
        if not log_channel:
            return

        # Skip if message is in mod category
        if mod_category and isinstance(mod_category, discord.CategoryChannel):
            if message.channel.category_id == mod_category.id:
                return

        # Proceed with logging
        embed = discord.Embed(
            color=discord.Color.red(),
        )

        files = []
        for attachment in message.attachments:
            files.append(await attachment.to_file())

        embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else None)
        embed.add_field(name="", value=f"{message.author.mention} deleted a message in {message.channel.mention}", inline=False)
        embed.add_field(name="", value=f"{message.content[:2000] or '*[No content]*'}", inline=False)
        await log_channel.send(embed=embed, silent=True)

        if files:
            await log_channel.send(files=files, silent=True)
