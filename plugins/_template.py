import discord, os, asyncio, argparse
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):
    
    init_term()

    # Cogs
    bot.add_cog(TemplateCog(bot))




#################################################################################




#################################################################################
# !template command
#################################################################################
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
    async def ping(self, ctx):
        # Put the bot response here




#################################################################################




#################################################################################
# Register terminal stuff
#################################################################################
def init_term():

    # Init some text we'll use later
    usage = "command_name [-args] [guild_id:optional]"
    
    example = """
    Usage example goes here
    """

    def function(args: list[str]):

        # Put the terminal response function here
        print("todo")

    # Help page & register
    register_plugin(
        name="template",
        help=f"""
template: {usage}
    Put the description here

    Options:
        --args           Explanation of arg

    Extra information here

    Usage:
{example}


""",
        func=function
    )