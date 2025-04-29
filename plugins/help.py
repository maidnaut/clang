import discord
import os
from discord.ext import commands

# Elevated permission roles
ALUMNI_ROLE = int(os.getenv("alumniRole"))
MODERATOR_ROLE = int(os.getenv("moderatorRole"))
ADMIN_ROLE = int(os.getenv("adminRole"))
OPERATOR_ROLE = int(os.getenv("operatorRole"))
ROOT_ROLE = int(os.getenv("rootRole"))

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):

        author = ctx.author
        author_roles = [role.id for role in author.roles]

        text = "These are all the commands available to you.\n\n"

        text += '''``!cookies`` Shows your cookies and supplies commands.
``!nom`` Eats a cookie
``!give <user>`` Gives the mentioned user one of your cookies.
``!transfer <user> (amount)`` Cookie credit transfer.
``!whois <user>`` Displays user info
``!avatar <user:optional>`` Shows the user's avatar
``!serverinfo`` Basic server stats
``!fortune``
'''

        # Is alumni
        if ALUMNI_ROLE in author_roles:
            text += '''``!warn <user> [reason]`` Creates a note and dm's them the warning
``!warnings <user>`` Shows all notes a user has
``!mute <user> [reason]`` Throws them in the ⁠mute-lounge 
``!unmute <user>`` Unmutes them
'''

        # Is mod
        if OPERATOR_ROLE in author_roles:
            text += '''``!op`` You must always have this enabled to mute and ban
``!warn <user> [reason]`` Creates a note and dm's them the warning
``!delwarn <user>`` Opens the warning deletion prompt
``!warnings <user>`` Shows all warnings a user has
``!clearwarns <user>`` Deletes all warnings a user has
``!mute <user> [reason]`` Throws them in the ⁠mute-lounge 
``!unmute <user>`` Unmutes them
``!ban <user> [reason]`` Please always provide reasons for bans
``!unban <user>`` Unbans a user
``!avatar`` Gets an avatar
``!promote <user> <role>`` Levels up a users perms, can be used multiple times
``!demote <user> <role>`` Demotes, can't be used on users with the same rank as you
'''

        # Is Admin
        if ROOT_ROLE in author_roles:
            text += '''``!op`` You must always have this enabled to mute and ban
``!warn <user> [reason]`` Creates a note and dm's them the warning
``!delwarn <user>`` Opens the warning deletion prompt
``!warnings <user>`` Shows all warnings a user has
``!clearwarns <user>`` Deletes all warnings a user has
``!mute <user> [reason]`` Throws them in the ⁠mute-lounge 
``!unmute <user>`` Unmutes them
``!ban <user> [reason]`` Please always provide reasons for bans
``!unban <user>`` Unbans a user
``!avatar`` Gets an avatar
``!promote <user>`` Levels up a users perms, can be used multiple times
``!demote <user>`` Demotes, can't be used on users with the same rank as you
``!setrate <int>`` Sets the random chance to gain a cookie on each message.
``!airdrop <user> (amount)`` Spawn cookies out of thin air to give to a user. Don't do this tho.
'''

        await ctx.send(text)

# This setup function adds the cog to the bot
def setup(bot):
    bot.add_cog(HelpCog(bot))
