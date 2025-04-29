import discord
import os
from discord.ext import commands

class ClnagCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clnag(self, ctx):
        user = ctx.author

        await ctx.send(f"haha {user.name} said clnag")

# This setup function adds the cog to the bot
def setup(bot):
    bot.add_cog(ClnagCog(bot))
