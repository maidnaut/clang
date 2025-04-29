# This is a basic error handling command to ignore commands not registered

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

class ErrorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return
        raise error

def setup(bot):
    bot.add_cog(ErrorCog(bot))
