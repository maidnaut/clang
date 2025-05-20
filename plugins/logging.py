import discord, time
from inc.utils import *
from datetime import datetime
from discord.ext import commands
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

    # On edit
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        # Drop out if in dm's
        if not before.guild or before.author.bot or before.content == after.content:
            return
            
        if before.author.bot or before.content == after.content:
            return

        channel = await get_channel(int(before.guild.id), "logs")

        if channel is not None:
            embed = discord.Embed(
                color=discord.Color.orange(),
            )

            embed.set_thumbnail(url=before.author.avatar.url if before.author.avatar else None)
            embed.add_field(name="", value=f" {before.author.mention} edited a message in {before.channel.mention}", inline=False)
            embed.add_field(name="", value=f"**Message Link:** [Jump to Message]({before.jump_url})", inline=False)
            embed.add_field(name="Before", value=before.content[:1024], inline=False)
            embed.add_field(name="After", value=after.content[:1024], inline=False)
            await channel.send(embed=embed, silent=True)

    # On delete
    @commands.Cog.listener()
    async def on_message_delete(self, message):

        # Drop out if dm's or bot
        if not message.guild or message.author.bot:
            return

        self.recent_deletions[message.channel.id].append(
            (message.id, time.monotonic())
        )

        await asyncio.sleep(0.5)
        is_tupper = False

        async for msg in message.channel.history(limit=3):
            if msg.webhook_id and (time.monotonic() - msg.created_at.timestamp()) < 2:
                is_tupper = True
                break

        channel_type = "botlogs" if is_tupper else "logs"
        channel = await get_channel(int(message.guild.id), channel_type)
        
        if channel:
            embed = discord.Embed(
                color=discord.Color.purple() if is_tupper else discord.Color.red(),
            )

            embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else None)
            embed.add_field(name="", value=f"{f'Tupperbox deleted a message by {message.author.mention}' if is_tupper else f'{message.author.mention} deleted a message'} in {message.channel.mention}", inline=False)
            embed.add_field(name="", value=f"{message.content[:2000] or '*[No content]*'}", inline=False)
            await channel.send(embed=embed, silent=True)