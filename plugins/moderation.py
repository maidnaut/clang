import discord, asyncio, datetime, io
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
            "delwarn": {
                "args": "<user> <warn id>",
                "desc": "Removes the specified warning from a user.",
                "perm": ["mod", "admin"]
            },
            "clear": {
                "args": "<user>",
                "desc": "Removes all warnings from a user.",
                "perm": ["mod", "admin"]
            },
            "ban": {
                "args": "<user> <time:optional> <reason>",
                "desc": "Bans a user from the server and dm's them the reason. If no time is provided, time will default to permanent",
                "perm": ["mod", "admin"]
            },
            "silentban": {
                "args": "<user>",
                "desc": "Silently bans a user from the server. If no time is provided, time will default to permanent",
                "perm": ["mod", "admin"]
            },
            "unbanban": {
                "args": "<user> <reason>",
                "desc": "Unbans the user from the server.",
                "perm": ["mod", "admin"]
            },
            "purgeban": {
                "args": "<user>",
                "desc": "Silently perma bans the user from the server and removes all their messages.",
                "perm": ["mod", "admin"]
            },
            "promote": {
                "args": "<user> <role>",
                "desc": "Promotes user to the selected role.",
                "perm": ["admin"]
            },
            "demote": {
                "args": "<user> <role>",
                "desc": "Removes the selected role from the user.",
                "perm": ["admin"]
            },
            "fire": {
                "args": "<user>",
                "desc": "Removes the user from staff entirely.",
                "perm": ["admin"]
            },
            "slowmode": {
                "args": "<user> <time>",
                "desc": "Sets the slowmode for the current channel.",
                "perm": ["submod", "mod", "admin"]
            },
        }

        # Init the table
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

    # modlog channel
    async def get_modlog_channel(self, ctx):
        try:
            guild_id = ctx.guild.id
            settings = db_read("logchans", [f"guild_id:{guild_id}", f"name:modlog"])
            if not settings or not settings[0][3]:
                return None
            
            channel_id = int(settings[0][3])
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                try:
                    channel = await guild.fetch_channel(channel_id)
                except discord.NotFound:
                    await ctx.send(f"Modlog channel {channel_id} not found in guild {guild_id}")
                    return None
            
            return channel
        except Exception as e:
            await ctx.send(f"Error getting modlog channel: {e}")
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




    # !elevation command
    @commands.command()
    async def elevation(self, ctx, status: str = None):
        
        user_level = await get_level(ctx)
        guild_id = ctx.guild.id
        author = ctx.author
        owner = ctx.guild.owner

        if user_level >= 4 or author == owner:
            if status == "on":
                db_update("config", [f"guild_id:{guild_id}", f"name:elevation_enabled"], [("enabled", "y")])
                await ctx.send(f"{author.mention} Elevation is now required on this server.")
            if status == "off":
                db_update("config", [f"guild_id:{guild_id}", f"name:elevation_enabled"], [("enabled", "n")])
                await ctx.send(f"{author.mention} Elevation is now disabled on this server.")




    # !setrole command
    @commands.command()
    async def setrole(self, ctx, role: str = None, *, id: str = None):
        
        user_level = await get_level(ctx)
        author = ctx.author
        guild_id = ctx.guild.id
        owner = ctx.guild.owner

        if user_level >= 4 or author == owner:

            roles = ["jail", "submod", "mod", "op", "admin", "root", "bots"]

            if not role:
                await ctx.send(f"{author.mention} Please select a role: `jail, submod, mod, op, admin, root` \n-# !setrole <role> <id>")
                return
            
            if not id:
                await ctx.send(f"{author.mention} Please provide an ID \n-# !setrole <role> <id>")
                return

            if role not in roles:
                await ctx.send(f"{author.mention} Please select a valid role: `jail, submod, mod, op, admin, root` \n-# !setrole <role> <id>")
                return

            if not id.isdigit():
                await ctx.send(f"{author.mention} Please provide a valid role ID \n-# !setrole <rold> <id>")
                return

            db_update("roles", [f"guild_id:{guild_id}", f"name:{role}"], [("role", id)])
            await ctx.send(f"{author.mention} {role} role set!")




    # !setchannel command
    @commands.command()
    async def setchannel(self, ctx, channel: str = None, *, id: str = None):

        user_level = await get_level(ctx)
        author = ctx.author
        guild_id = ctx.guild.id
        owner = ctx.guild.owner

        if user_level >= 4 or author == owner:

            channels = ["ticket_category", "joinlog", "logs", "modlog", "ticketlog", "admin_ticketlog", "jaillog", "jail_category"]

            if not channel:
                await ctx.send(f"{author.mention} Please select a channel or category: `ticket_category, joinlog, logs, modlog, ticketlog, admin_ticketlog` \n-# !setchannel <channel> <id>")
                return
            
            if not id:
                await ctx.send(f"{author.mention} Please provide an ID \n-# !setchannel <channel> <id>")
                return

            if channel not in channels:
                await ctx.send(f"{author.mention} Please select a valid channel or category: `ticket_category, joinlog, logs, modlog, ticketlog, admin_ticketlog` \n-# !setchannel <channel> <id>")
                return

            if not id.isdigit():
                await ctx.send(f"{author.mention} Please provide a valid channel or category ID \n-# !setchannel <channel> <id>")
                return

            db_update("logchans", [f"guild_id:{guild_id}", f"name:{channel}"], [("channel", id)])
            await ctx.send(f"{author.mention} {channel} channel set!")
                        



    # !op command
    @commands.command()
    async def op(self, ctx):
        
        # If elev is off, drop out, don't need to !op
        elev = db_read("config", [f"guild_id:{ctx.guild.id}", "name:elevation_enabled"])
        if elev and elev[0][3] == "n":
            await ctx.send(f"{ctx.author.mention} You don't need to op here!")
            return

        user = ctx.author
        user_level = await get_level(ctx)

        # Get the roles
        roles = {}
        role_list = db_read("roles", [f"guild_id:{ctx.guild.id}", "role:*"])
        for row in role_list:
            name, role_id = row[2], row[3]
            if role_id:
                roles[name] = int(role_id)

        # Validate
        if not roles.get("op") or not roles.get("root"):
            return await ctx.send(f"{ctx.author.mention} This server's roles aren't configured properly.")

        # Target the role
        if user_level == 2 and "op" in roles:
            target_id = roles["op"]
        elif user_level == 4 and "root" in roles:
            target_id = roles["root"]
        elif user_level == 5 and "root" in roles:
            target_id = roles["root"]
        else:
            return await ctx.send(f"{ctx.author.mention} This server's roles aren't configured properly.")

        # Get the object
        role_obj = ctx.guild.get_role(target_id)
        if not role_obj:
            return await ctx.send(f"{ctx.author.mention} This server's roles aren't configured properly.")

        # Hand out the role
        if role_obj not in user.roles:
            await user.add_roles(role_obj)
            await ctx.send(f"{ctx.author.mention} pulled out the ban hammer!")
        else:
            await user.remove_roles(role_obj)
            await ctx.send(f"{ctx.author.mention} put the ban hammer away.")




    # warn/silentwarn code
    async def _handle_warning(self, ctx, user_str: str = None, reason: str = None, silent: bool = False):

        user_level = await get_level(ctx)
        if user_level < 1: # Submod or higher
            return

        if not user_str:
            await ctx.send(f"{ctx.author.mention} Please provide a user. `!{'silent' if silent else ''}warn <user> <reason>`")
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

            now = datetime.datetime.now()

            last_warn = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
            warn_id = int(last_warn[-1][3]) + 1 if last_warn else 1
            
            db_insert("warnings",
                    ["guild_id", "user_id", "warn_id", "reason", "moderator_id", "warn_date"],
                    [int(ctx.guild.id), int(user.id), int(warn_id), reason, int(ctx.author.id), str(now)])

        # Database is busted?
        except Exception as e:
            await ctx.send(f"{user.mention} Something went wrong, I couldn't process the warning in my database.")
            await ctx.send(f"Database error: {e}")
            return

        # Send the embed
        try:
            modlog = await self.get_modlog_channel(ctx)
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
            await ctx.send(f"Modlog error: {e}")

        # Send the DM
        dm_status = ""
        if not user.bot and not silent:
            try:
                dm_embed = discord.Embed(
                    title=f"You were warned in {ctx.guild.name}",
                    color=discord.Color.orange(),
                    description=(
                        f"**Reason:** {reason}\n\n"
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

    # !delwarn
    @commands.command()
    async def delwarn(self, ctx, user_str: str = None, id: str = None):

        user_level = await get_level(ctx)
        if user_level not in (3, 5): # Op or Root
            await ctx.send("!op?")
            return

        if not user_str:
            await ctx.send(f"{ctx.author.mention} Please provide a user. `!delwarn <user> <id>`")
            return
        
        if not id:
            await ctx.send(f"{ctx.author.mention} Please provide a reason: `!delwarn <user> <reason>`")
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

        warnings = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
        if not warnings:
            await ctx.send(f"{ctx.author.mention} User has no warnings.")
            return

        try:
            db_remove("warnings",
                ["guild_id", "user_id", "warn_id",],
                [int(ctx.guild.id), int(user.id), int(id)])

            await ctx.send(f"{ctx.author.mention} Warning #{id} removed from {user.mention}'s wrap sheet.")
        
        except Exception as e:
            await ctx.send(f"Couldn't delete warning: {e}")
            
    # !clear
    @commands.command()
    async def clear(self, ctx, user_str: str = None):

        user_level = await get_level(ctx)
        
        if user_level not in (3, 5): # Op or Root
            await ctx.send("!op?")
            return

        if not user_str:
            await ctx.send(f"{ctx.author.mention} Please provide a user. `!clear <user>`")
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

        warnings = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
        if not warnings or len(warnings) == 0:
            await ctx.send(f"{ctx.author.mention} User has no warnings.")
            return

        try:
            for warning in warnings:

                warn_id = warning[3]
                db_remove("warnings",
                    ["guild_id", "user_id", "warn_id"],
                    [int(ctx.guild.id), int(user.id), int(warn_id)])

            await ctx.send(f"{ctx.author.mention} All warnings removed from {user.mention}'s wrap sheet.")
        
        except Exception as e:
            await ctx.send(f"Couldn't delete warnings: {e}")
            
        


