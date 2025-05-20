import discord
from inc.utils import *
from datetime import datetime
from discord.ext import commands




def setup(bot):
    bot.add_cog(LoggingCog(bot))




class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            embed.add_field(name="User", value=f"{member.mention} {member.name}", inline=True)

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
            embed.add_field(name="User", value=f"{member.mention} {member.name}", inline=True)

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
                title=f"Message Edited in {before.channel.mention}",
                description=f"**Author:** {before.author.mention}",
                color=discord.Color.orange(),
            )

            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.add_field(name="User", value=f"{member.mention} {member.name}", inline=False)
            embed.add_field(name="Message Link", value=f"[Jump to Message]({before.jump_url})", inline=False)
            embed.add_field(name="Before", value=before.content[:1024], inline=False)
            embed.add_field(name="After", value=after.content[:1024], inline=False)
            await channel.send(embed=embed, silent=True)

    # On delete
    @commands.Cog.listener()
    async def on_message_delete(self, message):

        # drop out if in dm's
        if not message.guild:
            return
            
        if message.author.bot and not message.webhook_id:
            return

        # Check if it's a bot
        if message.webhook_id:
            
            channel = await get_channel(int(message.guild.id), "botlogs")

            if channel is not None:
                embed = discord.Embed(
                    title=f"Bot Message Deleted in {message.channel.mention}",
                    color=discord.Color.purple(),
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                embed.add_field(name="User", value=f"{member.mention} {member.name}", inline=False)
                embed.add_field(name="Content", value=f"**Message:** {message.content[:2000]}", inline=False)
                await channel.send(embed=embed, silent=True)
        else:
        
            channel = await get_channel(int(message.guild.id), "logs")

            if channel is not None:
                embed = discord.Embed(
                    title=f"Message Deleted in {message.channel.mention}",
                    color=discord.Color.dark_red(),
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                embed.add_field(name="User", value=f"{member.mention} {member.name}", inline=False)
                embed.add_field(name="Content", value=f"**Message:** {message.content[:2000]}", inline=False)
                await channel.send(embed=embed, silent=True)