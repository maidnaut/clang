import discord, os, asyncio, argparse
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *

#################################################################################
# Init
#################################################################################

def setup(bot):
    
    init_term()

    # Cogs
    bot.add_cog(PingCog(bot))
    bot.add_cog(ServerInfoCog(bot))
    bot.add_cog(AvatarCog(bot))




#################################################################################




#################################################################################
# !ping
#################################################################################
class PingCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # !help info
        self.__help__ = {
            "ping": {
                "args": "",
                "desc": "Responds with Pong!",
                "perm": "everyone"
            }
        }

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

#################################################################################
# !serverinfo
#################################################################################
class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # !help info
        self.__help__ = {
            "serverinfo": {
                "args": "",
                "desc": "Displays server data",
                "perm": "everyone"
            }
        }

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])

        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=""
        )

        if guild.icon:
            icon_url = str(guild.icon)
            embed.set_author(name=guild.name, icon_url=icon_url)
            embed.set_thumbnail(url=icon_url)
        else:
            embed.set_author(name=guild.name)
        
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Creation", value=f"{guild.created_at.strftime("%b %d %Y")} - ", inline=True)
        embed.add_field(name="Members", value=f"{guild.member_count}", inline=True)
        await ctx.send(embed=embed)

#################################################################################
# !avatar
#################################################################################
class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # !help info
        self.__help__ = {
            "avatar": {
                "args": "<user:optional>",
                "desc": "Displays an avatar",
                "perm": "everyone"
            }
        }

    @commands.command()
    async def avatar(self, ctx, *, user_input: str = None):
        if user_input is None:
            user = ctx.author
        else:
            if ctx.message.mentions:
                user = ctx.message.mentions[0]
            elif user_input.isdigit():
                try:
                    user = await self.bot.fetch_user(int(user_input))
                    member = ctx.guild.get_member(user.id)
                    if member:
                        user = member
                except discord.NotFound:
                    user = None
                except discord.HTTPException:
                    user = None
            else:
                user = None

        if user is None:
            await ctx.send(f"I have no record for that user.")
            return

        embed = discord.Embed(
            color=discord.Color.blurple(),
            description=f"**{user.mention}** (`{user.name}`)"
        )

        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)




#################################################################################




#################################################################################
# Handle shell commands and help page
#################################################################################
def init_term():

    # Init some text we'll use later
    usage = "utils [-e | -d [module] | -s [module] [role]] [guild_id:optional]"
    
    example = """
    utils [-e/-d] [module] [guild:optional]
    utils [-set] [module] [everyone / submod / mods / admins] [guild:optional]
    """

    modules = ["ping", "serverinfo", "avatar", "whois"]
    roles = ["e", "s", "m", "a", "everyone", "submod", "mod", "admin"]
    role_names = {"e": "everyone", "s": "submod", "m": "mod", "a": "admin"}

    def function(args: list[str]):

        # Default option if no arguments are provided, 
        def print_status(guild=None):
            header = f"Utils are enabled in {'guild ' + guild if guild else 'your server'}"
            print(f"{usage}\n", highlight=False)

        if not args:
            print_status()
            return

        first = args[0]

        if first.startswith("-"):
            action_map = {
                "-e": "enable", "--enable": "enable",
                "-d": "disable", "--disable": "disable",
                "-s": "set", "--set": "set"
            }
            action = action_map.get(first)
            if not action:
                print(f"Error: unrecognized argument '{first}'\nUsage: {usage}\n", markup=False)
                return

            extras = args[1:]
            module = role = guild = None

            if action == "set":
                if len(extras) < 1:
                    print(f"Error: '-s' requires a module\nUsage: {usage}\n", markup=False)
                    return
                module = extras[0]
                if module not in modules:
                    module_list = ", ".join(modules)
                    print(f"Error: That module doesn't exist. Modules: {module_list}\n", markup=False)
                    return

                if len(extras) < 2:
                    print(f"Error: '-s' requires a role - [(e)veryone, (s)ubmod), (m)od, (a)dmin]\n")
                    return
                role = extras[1]
                if role not in roles:
                    print(f"Error: Incorrect role - [(e)veryone, (s)ubmod), (m)od, (a)dmin]\n")
                    return

                if len(extras) > 2:
                    if extras[2].isdigit():
                        guild = extras[2]
                    else:
                        print(f"Error: Invalid guild ID '{extras[2]}'\nUsage: {usage}\n", markup=False)
                        return

                _role = role_names.get(role, role)
                target = f"for guild {guild}" if guild else "in utils"
                print(f"Setting role '{_role}' on module '{module}' {target}\n")
                return

            if extras:
                module = extras[0]
                if module not in modules:
                    print(f"Error: That module doesn't exist\nUsage: {usage}\n", markup=False)
                    return
                if len(extras) > 1:
                    if extras[1].isdigit():
                        guild = extras[1]
                    else:
                        print(f"Error: Invalid guild ID '{extras[1]}'\nUsage: {usage}\n", markup=False)
                        return

            target = f"module '{module}' for guild {guild}" if guild and module else \
                    f"module '{module}' in utils" if module else "utils globally"
            print(f"{action.capitalize()}ing {target}\n")
            return

        if first.isdigit():
            print_status(guild=first)
        else:
            print(f"Error: unrecognized argument '{first}'\nUsage: {usage}\n", markup=False)

    # Help page & register
    register_plugin(
        name="utils",
        help=f"""
utilities: {usage}
    Edit the utilities configuration.

    Options:
        --enable         Enables the module
        --disable        Disables the module
        --set            Updates the config for the module to the specified role

    The default command without any options shows the status and configs of all modules inside the plugin.
    Enabling/disabling without the module specified will toggle the status of the whole plugin.
    Note: If Clang is in multiple servers, specifying the guild is required otherwise it'll complain at you.

    Modules: ping, avatar, serverinfo, whois

    Usage:
{example}


""",
        func=function
    )