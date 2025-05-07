import discord, asyncio, datetime
from datetime import timedelta
from typing import Optional
from discord.ext import commands
from discord.utils import get
from inc.utils import *

#################################################################################
# Initial setup for the mod suite
#################################################################################

def setup(bot):
    bot.add_cog(ModerationCog(bot))




#################################################################################




#################################################################################
# Moderation command suite
#################################################################################
class ModerationCog(commands.Cog):

    # Bot init & build help sheet
    def __init__(self, bot):
        self.bot = bot
        self.__help__ = {
            "op": {
                "args": "",
                "desc": "Grants elevated perms. Must always be activated to mute and ban",
                "perm": ["mod", "admin"]
            },
            "warn": {
                "args": "<user> <reason>",
                "desc": "Issues and dm's a warning to a user.",
                "perm": ["submod", "mod", "admin"]
            },
            "silentwarn": {
                "args": "<user> <reason>",
                "desc": "Silently issues a warning to a user without a dm.",
                "perm": ["submod", "mod", "admin"]
            },
            "whois": {
                "args": "<user:optional>",
                "desc": "Displays user data",
                "perm": "everyone"
            },
        }

    # Get the channel to log stuff in
    async def get_modlog_channel(self, guild):
        """Retrieve modlog channel with proper type handling"""
        try:
            settings = db_read("guild_settings", [f"guild_id:{guild.id}"])
            if not settings or not settings[0][2]:
                return None
            
            channel_id = int(settings[0][2])
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                try:
                    channel = await guild.fetch_channel(channel_id)
                except discord.NotFound:
                    print(f"Modlog channel {channel_id} not found in guild {guild.id}")
                    return None
            
            return channel
        except Exception as e:
            print(f"Error getting modlog channel: {e}")
            return None


    # Handle errors
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "reason":
                await ctx.send(f"Please provide a reason. Usage: `!{ctx.command.name} @user <reason>`")
            elif error.param.name == "user":
                await ctx.send(f"Please mention a user. Usage: `!{ctx.command.name} @user <reason>`")
            return
        
        return await self.bot.on_command_error(ctx, error)

    # !op command
    @commands.command()
    async def op(self, ctx):
        
        # Is elevation enabled?
        elev = db_read("config", [f"guild_id:{ctx.guild.id}", "name:elevation_enabled"])
        if elev[0][3] == "n":
            await ctx.send(f"{user.mention} You don't need to op!")
            return

        # Set up our op data
        user = ctx.author
        user_level = await get_level(ctx)
        roles = {}
        role_list = db_read("roles", [f"guild_id:{ctx.guild.id}", "role:*"])
        for row in role_list:
            name_col, id_col = row[2], row[3]
            if id_col:
                key = name_col
                roles[key] = int(id_col)

        if user_level == 2 and "op_role" in roles:
            if not get(ctx.guild.roles, id=roles["op_role"]):
                return await ctx.send(f"{user.mention} This servers roles aren't configured properly.")
            target_id = roles["op_role"]
        elif user_level == 4 and "root_role" in roles:
            if not get(ctx.guild.roles, id=roles["root_role"]):
                return await ctx.send(f"{user.mention} This servers roles aren't configured properly.")
            target_id = roles["root_role"]
        else:
            return


        role_obj = ctx.guild.get_role(target_id)
        if not role_obj:
            return await ctx.send(f"{user.mention} You don't need to op here!")

        if role_obj not in user.roles:
            await user.add_roles(role_obj)
            await ctx.send(f"{user.mention} pulled out the ban hammer!")
        else:
            await user.remove_roles(role_obj)
            await ctx.send(f"{user.mention} put the ban hammer away.")




    # warn/silentwarn code
    async def _handle_warning(self, ctx, user_str: str = None, reason: str = None, silent: bool = False):

        if not await has_perms(ctx):
            return

        if not user_str:
            await ctx.send(f"{ctx.author.mention} Please mention a user. `!{'silent' if silent else ''}warn <user> <reason>`")
            return
        
        if not reason:
            await ctx.send(f"{ctx.author.mention} Please provide a reason: `!{'silent' if silent else ''}warn <user> <reason>`")
            return

        try:
            # First try as member
            user = await commands.MemberConverter().convert(ctx, user_str)
        except commands.MemberNotFound:
            try:
                # Then try as global user
                user = await commands.UserConverter().convert(ctx, user_str)
                silent = True
            except commands.UserNotFound:
                await ctx.send(f"{ctx.author.mention} Couldn't find user: {user_str}")
                return

        # Do the warn
        try:

            if not table_exists("warnings"):
                new_db("warnings", [
                    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                    ("guild_id", "INTEGER"),
                    ("user_id", "INTEGER"),
                    ("warn_id", "INTEGER"),
                    ("reason", "TEXT"),
                    ("moderator_id", "INTEGER"),
                    ("warn_date", "TEXT"),
                ])

            now = datetime.datetime.now()

            last_warn = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
            warn_id = int(last_warn[0][2]) + 1 if last_warn else 1
            
            db_insert("warnings",
                    ["guild_id", "user_id", "warn_id", "reason", "moderator_id", "warn_date"],
                    [int(ctx.guild.id), int(user.id), int(warn_id), reason, int(ctx.author.id), str(now)])

        # Database is busted?
        except Exception as e:
            await ctx.send(f"{user.mention} Something went wrong, I couldn't process the warning in my database.")
            print(f"Database error: {e}")
            return

        # Send the embed
        try:
            #modlog = await self.get_modlog_channel(ctx.guild)
            modlog = ctx.guild.get_channel(1366546228371787912)
            if modlog:
                embed = discord.Embed(
                    color=discord.Color.orange(),
                    title="User Warned"
                )

                embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
                
                embed.add_field(name="", value="", inline=False)
                embed.add_field(name="User", value=f"{user.mention}", inline=True)
                embed.add_field(name="Mod", value=f"{ctx.author.mention}", inline=True)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                await modlog.send(embed=embed)

        except Exception as e:
            print(f"Modlog error: {e}")

        # Send the DM
        dm_status = ""
        if not user.bot and not silent:
            try:
                dm_embed = discord.Embed(
                    title=f"You were warned in {ctx.guild.name}",
                    color=discord.Color.orange(),
                    description=(
                        f"**Reason:** {reason}\n\n"
                        f"Please review server rules to avoid further actions."
                    )
                )
                dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else "")
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                dm_status = " (Couldn't DM user)"
            except Exception as e:
                dm_status = " (DM failed)"

        # Update your final response
        response = f"{ctx.author.mention} Done. {dm_status}"
        await ctx.send(response)

    # !warn
    @commands.command()
    async def warn(self, ctx, user: str = None, *, reason: str = None):
        await self._handle_warning(ctx, user, reason, silent=False)

    # !silentwarn
    @commands.command()
    async def silentwarn(self, ctx, user: str = None, *, reason: str = None):
        await self._handle_warning(ctx, user, reason, silent=True)


