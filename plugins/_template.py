import discord, os, asyncio, argparse
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *

def setup(bot):

    bot.add_cog(TemplateCog(bot))

class TemplateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # !help info
        self.__help__ = {
            "command_title": {
                "args": "",
                "desc": "This is the description given with !help",
                "perm": "everyone" # everyone, submod, mods, op, admin, root, owner
            }
        }

    @commands.command()
    async def template(self, ctx):
        # Put the bot response here