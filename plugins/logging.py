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
        guild_id = str(member.guild.id)
        joinlog = await get_channel(ctx.guild.id, "joinlog")
        
        channel = self.bot.get_channel(joinlog)

        if channel not "":
            embed = discord.Embed(
                title="🎉 Member Joined",
                description=f"{member.mention} {member.name}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await channel.send(embed=embed, silent=True)

    # Leave log
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = str(member.guild.id)
        joinlog = await get_channel(ctx.guild.id, "joinlog")
        
        channel = self.bot.get_channel(joinlog)

        if channel not "":
            embed = discord.Embed(
                title="👋 Member Left",
                description=f"{member.mention} {member.name}",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await channel.send(embed=embed, silent=True)

    # On edit
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        
        guild_id = str(member.guild.id)
        logs = await get_channel(ctx.guild.id, "logs")
        
        channel = self.bot.get_channel(logs)

        if channel not "":
            embed = discord.Embed(
                title="Message Edited",
                description=f"**Author:** {before.author.mention}\n**Channel:** {before.channel.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Before", value=before.content[:1024], inline=False)
            embed.add_field(name="After", value=after.content[:1024], inline=False)
            await channel.send(embed=embed, silent=True)

    # On delete
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot and not message.webhook_id:
            return

        # Check if it's a bot
        if message.webhook_id:
        
            guild_id = str(member.guild.id)
            botlogs = await get_channel(ctx.guild.id, "botlogs")
            channel = self.bot.get_channel(botlogs)

            if channel not "":
                embed = discord.Embed(
                    title="Bot Message Deletion",
                    description=f"**Channel:** {message.channel.mention}\n**Content:** {message.content[:2000]}",
                    color=discord.Color.purple(),
                    timestamp=datetime.now()
                )
                await channel.send(embed=embed, silent=True)
        else:
        
            guild_id = str(member.guild.id)
            logs = await get_channel(ctx.guild.id, "logs")
            channel = self.bot.get_channel(logs)

            if channel not "":
                embed = discord.Embed(
                    title="Message Deleted",
                    description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}",
                    color=discord.Color.dark_red(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Content", value=message.content[:2000] or "[Content Unavailable]")
                await channel.send(embed=embed, silent=True)