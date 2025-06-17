import discord, datetime, re, typing
from typing import Optional
from discord.ext import commands, tasks
from inc.utils import *

#################################################################################
# Init
#################################################################################

def setup(bot):
    bot.add_cog(ModerationCog(bot))




#################################################################################




#################################################################################
# Mod Suite
#################################################################################
class ModerationCog(commands.Cog):
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
                "desc": "(Alias: !addnote) Silently issues a warning to a user without a dm.",
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
            "purgeban": {
                "args": "<user> <reason>",
                "desc": "Bans a user from the server and deletes up to 7 days worth of messages",
                "perm": ["mod", "admin"]
            },
            "unban": {
                "args": "<user> <reason>",
                "desc": "Unbans the user from the server.",
                "perm": ["mod", "admin"]
            },
            "purge": {
                "args": "<user> <amount>",
                "desc": "Deletes up to 100 messages from the user in the channel the command is run",
                "perm": ["mod", "admin"]
            },
            "slowmode": {
                "args": "<time>",
                "desc": "(Alias: !slow) Sets the slowmode for the current channel. Takes s/m/d for time, and accepts 0 or off to disable.",
                "perm": ["submod", "mod", "admin"]
            },
            "timeout": {
                "args": "<user> <time> <reason:optional>",
                "desc": "(Alias: !mute) Times out a user for the set amount of time, dming them the reason",
                "perm": ["submod", "mod", "admin"]
            }
        }

        # Ensure our tables exist
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
        if not table_exists("bans"):
            new_db("bans", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER"),
                ("user_id", "INTEGER"),
                ("ban_date", "TEXT"),
                ("unban_date", "TEXT"),
            ])

        # Start unban loop
        if not self.unban_loop.is_running():
            self.unban_loop.start()




    # !op command
    @commands.command()
    async def op(self, ctx):
        
        # If elev is off, drop out, don't need to !op
        elev = db_read("config", [f"guild_id:{ctx.guild.id}", "name:elevation_enabled"])
        if elev and elev[0][3] == "n":
            await ctx.send(f"{await author_ping(ctx)} You don't need to op here!")
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
            return await ctx.send(f"{await author_ping(ctx)} This server's roles aren't configured properly.")

        # Target the role
        if user_level == 2 and "op" in roles:
            target_id = roles["op"]
        elif user_level == 3 and "op" in roles:
            target_id = roles["op"]
        elif user_level == 4 and "root" in roles:
            target_id = roles["root"]
        elif user_level == 5 and "root" in roles:
            target_id = roles["root"]
        else:
            # User is not staff, ignore
            return

        # Get the object
        role_obj = ctx.guild.get_role(target_id)
        if not role_obj:
            return await ctx.send(f"{await author_ping(ctx)} This server's roles aren't configured properly.")

        # Hand out the role
        if role_obj not in user.roles:
            await user.add_roles(role_obj)
            await ctx.send(f"Oh shit, {await author_ping(ctx)}'s got a glock. EVERYBODY DOWN")
        else:
            await user.remove_roles(role_obj)
            await ctx.send(f"{await author_ping(ctx)} put the glock away.")



    # warn/silentwarn code
    async def _handle_warning(self, ctx, user_str: str = None, reason: str = None, silent: bool = False):

        user_level = await get_level(ctx)
        if user_level < 1:
            return

        if not user_str:
            await ctx.send(f"{await author_ping(ctx)} Please provide a user. `!{'silent' if silent else ''}warn <user> <reason>`")
            return
        
        if not reason:
            await ctx.send(f"{await author_ping(ctx)} Please provide a reason: `!{'silent' if silent else ''}warn <user> <reason>`")
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
                await ctx.send(f"{await author_ping(ctx)} Couldn't find user: {user_str}")
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
            await ctx.send(f"{await author_ping(ctx)} Something went wrong, I couldn't process the warning in my database.")
            await ctx.send(f"Database error: {e}")
            return

        # Send the embed
        try:
            modlog = await get_channel(ctx.guild.id, "modlog")
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
        response = f"{await author_ping(ctx)} Done. {dm_status}"
        await ctx.send(response)

    # !warn
    @commands.command()
    async def warn(self, ctx, user: str = None, *, reason: str = None):
        await self._handle_warning(ctx, user, reason, silent=False)

    # !silentwarn
    @commands.command(aliases=['addnote'])
    async def silentwarn(self, ctx, user: str = None, *, reason: str = None):
        await self._handle_warning(ctx, user, reason, silent=True)

    # !delwarn
    @commands.command()
    async def delwarn(self, ctx, user_str: str = None, id: str = None):

        user_level = await get_level(ctx)
        if user_level < 2:
            return

        if user_level not in (3, 5): # Op or Root
            await ctx.send("!op?")
            return

        if not user_str:
            await ctx.send(f"{await author_ping(ctx)} Please provide a user. `!delwarn <user> <id>`")
            return
        
        if not id:
            await ctx.send(f"{await author_ping(ctx)} Please provide a reason: `!delwarn <user> <reason>`")
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
                await ctx.send(f"{await author_ping(ctx)} Couldn't find user: {user_str}")
                return

        warnings = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
        if not warnings:
            await ctx.send(f"{await author_ping(ctx)} User has no warnings.")
            return

        try:
            db_remove("warnings",
                ["guild_id", "user_id", "warn_id",],
                [int(ctx.guild.id), int(user.id), int(id)])

            await ctx.send(f"{await author_ping(ctx)} Warning #{id} removed from {await user_ping(ctx, user)}'s rap sheet.")
        
        except Exception as e:
            await ctx.send(f"{await author_ping(ctx)} Couldn't delete warning: {e}")

    # !clear
    @commands.command()
    async def clear(self, ctx, user_str: str = None):

        user_level = await get_level(ctx)
        if user_level < 2:
            return

        if user_level not in (3, 5): # Op or Root
            await ctx.send("!op?")
            return

        if not user_str:
            await ctx.send(f"{await author_ping(ctx)} Please provide a user. `!clear <user>`")
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
                await ctx.send(f"{await author_ping(ctx)} Couldn't find user: {user_str}")
                return

        warnings = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
        if not warnings or len(warnings) == 0:
            await ctx.send(f"{await author_ping(ctx)} User has no warnings.")
            return

        try:
            for warning in warnings:

                warn_id = warning[3]
                db_remove("warnings",
                    ["guild_id", "user_id", "warn_id"],
                    [int(ctx.guild.id), int(user.id), int(warn_id)])

            await ctx.send(f"{await author_ping(ctx)} All warnings removed from {await user_ping(ctx, user)}'s rap sheet.")
        
        except Exception as e:
            await ctx.send(f"{await author_ping(ctx)} Couldn't delete warnings: {e}")




    # !ban
    @commands.command()
    async def ban(self, ctx, user_str: str = None, *, args: str = None):
        user_level = await get_level(ctx)
        if user_level < 2:
            return

        if not user_str or not args:
            return await ctx.send(f"{await author_ping(ctx)} Usage: `!ban <user> [time] <reason>`")

        # Get ban time
        tm = re.match(r"(?:(\d+)y)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?", args.split()[0])
        if tm and any(tm.groups()):
            ban_time = args.split()[0]
            reason   = " ".join(args.split()[1:])
        else:
            ban_time = None
            reason   = args

        if not reason:
            return await ctx.send(f"{await author_ping(ctx)} Please provide a reason.")

        # Find user
        try:
            user = await commands.MemberConverter().convert(ctx, user_str)
        except commands.MemberNotFound:
            try:
                user = await commands.UserConverter().convert(ctx, user_str)
            except commands.UserNotFound:
                return await ctx.send(f"{await author_ping(ctx)} Couldn't find `{user_str}`")

        # Already banned?
        try:
            if await ctx.guild.fetch_ban(discord.Object(id=user.id)):
                return await ctx.send(f"{await author_ping(ctx)} That user is already banned.")
        except discord.NotFound:
            pass
        except discord.Forbidden:
            return await ctx.send(f"{await author_ping(ctx)} Missing permission to check bans.")
        except discord.HTTPException as e:
            return await ctx.send(f"{await author_ping(ctx)} Error checking bans: {e}")

        # Figure out unban_date
        if ban_time:
            years = int(tm.group(1) or 0)
            days  = int(tm.group(2) or 0)
            hrs   = int(tm.group(3) or 0)
            mins  = int(tm.group(4) or 0)
            delta = datetime.timedelta(days=years*365 + days, hours=hrs, minutes=mins)
            unban_dt = (datetime.datetime.now() + delta).replace(microsecond=0)
        else:
            unban_dt = None

        now_iso = datetime.datetime.now().replace(microsecond=0).isoformat()

        # Setup for note
        now = datetime.datetime.now()
        last_warn = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
        warn_id   = int(last_warn[-1][3]) + 1 if last_warn else 1
        ban_note  = f"**BANNED**{' for '+ban_time if ban_time else ' permanently'}: {reason}"

        db_insert(
            "warnings",
            ["guild_id","user_id","warn_id","reason","moderator_id","warn_date"],
            [ctx.guild.id, user.id, warn_id, ban_note, ctx.author.id, now]
        )

        db_insert("bans", ["guild_id","user_id","ban_date","unban_date"], [ctx.guild.id, user.id, now_iso, unban_dt.isoformat() if unban_dt else None])

        # Do the ban
        try:
            if isinstance(user, discord.Member):
                await user.ban(reason=reason)
            else:
                await ctx.guild.ban(user, reason=reason)
        except discord.Forbidden:
            return await ctx.send(f"{await author_ping(ctx)} Missing permission to ban.")
        except discord.HTTPException as e:
            return await ctx.send(f"{await author_ping(ctx)} Ban failed: {e}")

        # Modlog embed
        modlog = await get_channel(ctx.guild.id, "modlog")
        if modlog:
            embed = discord.Embed(color=discord.Color.red(), title="User Banned")
            if getattr(user, "avatar", None):
                embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="User",   value=user.mention,      inline=True)
            embed.add_field(name="Mod",    value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason,            inline=False)
            await modlog.send(embed=embed)

        await ctx.send(f"{user.mention} banned{' for '+ban_time if ban_time else ''}. Reason: {reason}")

    # !unban
    @commands.command()
    async def unban(self, ctx, user_str: str = None, *, reason: str = None):
        user_level = await get_level(ctx)
        if user_level < 2:
            return

        if not user_str or not reason:
            return await ctx.send(f"{await author_ping(ctx)} Usage: `!unban <user> <reason>`")

        # Find user
        try:
            user = await commands.MemberConverter().convert(ctx, user_str)
        except commands.MemberNotFound:
            try:
                user = await commands.UserConverter().convert(ctx, user_str)
            except commands.UserNotFound:
                return await ctx.send(f"{await author_ping(ctx)} Couldn't find `{user_str}`")

        # Check ban exists
        try:
            await ctx.guild.fetch_ban(discord.Object(id=user.id))
        except discord.NotFound:
            return await ctx.send(f"{await author_ping(ctx)} That user isn't banned.")
        except discord.Forbidden:
            return await ctx.send(f"{await author_ping(ctx)} Missing permission to check bans.")
        except discord.HTTPException as e:
            return await ctx.send(f"{await author_ping(ctx)} Error checking bans: {e}")

        # Add unban note
        now = datetime.datetime.now()
        last_warn = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
        warn_id   = int(last_warn[-1][3]) + 1 if last_warn else 1
        note      = f"**UNBANNED:** {reason}"
        db_insert(
            "warnings",
            ["guild_id","user_id","warn_id","reason","moderator_id","warn_date"],
            [ctx.guild.id, user.id, warn_id, note, ctx.author.id, now]
        )

        db_remove("bans", ["guild_id", "user_id"], [ctx.guild.id, user.id])

        # Do the unban
        try:
            await ctx.guild.unban(user)
        except discord.Forbidden:
            return await ctx.send(f"{await author_ping(ctx)} Missing permission to unban.")
        except discord.HTTPException as e:
            return await ctx.send(f"{await author_ping(ctx)} Unban failed: {e}")

        # Modlog embed
        modlog = await get_channel(ctx.guild.id, "modlog")
        if modlog:
            embed = discord.Embed(color=discord.Color.purple(), title="User Unbanned")
            if getattr(user, "avatar", None):
                embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="User",   value=user.mention, inline=True)
            embed.add_field(name="Mod",    value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            await modlog.send(embed=embed)

        await ctx.send(f"{user.mention} unbanned. Reason: {reason}")

    # Unban loop
    @tasks.loop(minutes=1)
    async def unban_loop(self):

        now_iso = datetime.datetime.now().replace(microsecond=0).isoformat()

        expired = db_read("bans", [f"unban_date:<{now_iso}"])

        for row in expired:
            guild_id = int(row[1]); user_id = int(row[2])
            guild    = self.bot.get_guild(guild_id)
            if not guild:
                continue

            user = await self.bot.fetch_user(user_id)
            try:
                await guild.unban(user, reason="Ban timer expired")
            except discord.NotFound:
                print(f"\n[bold yellow][!][/bold yellow] User {user_id} was already unbanned.")
            except Exception as e:
                print(f"\n[!] Unban failed for {user_id}@{guild_id}: {e}")


            db_remove("bans", ["guild_id", "user_id"], [guild.id, user_id])

            # Log and unban
            now = datetime.datetime.now()
            last_warn = db_read("warnings", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
            warn_id   = int(last_warn[-1][3]) + 1 if last_warn else 1
            db_insert(
                "warnings",
                ["guild_id","user_id","warn_id","reason","moderator_id","warn_date"],
                [guild_id, user_id, warn_id, "**UNBANNED:** Ban timer expired", self.bot.user.name, now]
            )

            # Post to modlog
            modlog = await get_channel(guild.id, "modlog")
            if modlog:
                embed = discord.Embed(color=discord.Color.purple(), title="User Unbanned")
                if user.avatar:
                    embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name="User",   value=user.mention,      inline=True)
                embed.add_field(name="Mod",    value=self.bot.user.name,           inline=True)
                embed.add_field(name="Reason", value="Ban timer expired", inline=False)
                await modlog.send(embed=embed)





    # !purge
    @commands.command()
    async def purge(self, ctx, user_str: str = None, amount: str = None):
        user_level = await get_level(ctx)
        if user_level < 2:
            return

        # No user supplied
        if user_str == None:
            return await ctx.send(f"{await author_ping(ctx)} Supply a user: `!purge <user> <amount>`")

        if amount == None:
            return await ctx.send(f"{await author_ping(ctx)} Supply an amount: `!purge <user> <amount>`")
        
        amount = int(amount)

        if amount > 100:
            return await ctx.send(f"{await author_ping(ctx)} Max message deletion is 100: `!purge <user> <amount>`")

        # Find user
        try:
            user = await commands.MemberConverter().convert(ctx, user_str)
        except commands.MemberNotFound:
            try:
                user = await commands.UserConverter().convert(ctx, user_str)
            except commands.UserNotFound:
                return await ctx.send(f"{await author_ping(ctx)} Couldn't find user `{user_str}`")

        # Check permissions
        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            return await ctx.send(f"{await author_ping(ctx)} I need `Manage Messages` permission")

        # Purge messages
        total_deleted = 0
        remaining = amount
        def check(m): return m.author.id == user.id and m.id < ctx.message.id

        while remaining > 0:
            limit = min(remaining, 100)
            deleted = await ctx.channel.purge(limit=limit, check=check, before=ctx.message)
            count = len(deleted)
            total_deleted += count
            remaining -= count
            if count == 0:
                break

        # Post to modlog
        modlog = await get_channel(ctx.guild.id, "modlog")
        if modlog:
            embed = discord.Embed(color=discord.Color.purple(), title=f"{total_deleted} messages purged")
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="User",   value=user.mention,      inline=True)
            embed.add_field(name="Mod",    value=ctx.author.mention,           inline=True)
            embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=False)
            await modlog.send(embed=embed)

        msg = await ctx.send(f"{await author_ping(ctx)} Purged {total_deleted} messages from {user.mention}")





    # !purgeban
    @commands.command()
    async def purgeban(self, ctx, user_str: str = None, *, reason: str = None):
        user_level = await get_level(ctx)
        if user_level < 2:
            return

        if not user_str:
            return await ctx.send(f"{await author_ping(ctx)} Usage: `!purgeban <user> <reason>`")

        if not reason:
            reason = "No reason provided. Likely spam."

        # Find user
        try:
            user = await commands.MemberConverter().convert(ctx, user_str)
        except commands.MemberNotFound:
            try:
                user = await commands.UserConverter().convert(ctx, user_str)
            except commands.UserNotFound:
                return await ctx.send(f"{await author_ping(ctx)} Couldn't find user `{user_str}`")

        # Ban
        try:
            existing_ban = await ctx.guild.fetch_ban(user)
            if existing_ban:
                return await ctx.send(f"{await author_ping(ctx)} User already banned! Run !purge instead.")
        except discord.NotFound:
            pass
        except discord.Forbidden:
            return await ctx.send(f"{await author_ping(ctx)} Can't check bans!")
        except discord.HTTPException as e:
            return await ctx.send(f"{await author_ping(ctx)} Error checking bans: {e}")

        # Add note
        now = datetime.datetime.now()
        ban_note = f"**PURGE BANNED**: {reason}"
        
        last_warn = db_read("warnings", [f"user_id:{user.id}", f"guild_id:{ctx.guild.id}"])
        warn_id = int(last_warn[-1][3]) + 1 if last_warn else 1
        
        db_insert("warnings",
            ["guild_id", "user_id", "warn_id", "reason", "moderator_id", "warn_date"],
            [ctx.guild.id, user.id, warn_id, ban_note, ctx.author.id, now]
        )

        # PURGEBAN
        try:
            await ctx.guild.ban(user, reason=reason, delete_message_seconds=604800)
        except discord.Forbidden:
            return await ctx.send(f"{await author_ping(ctx)} Missing ban permissions")
        except discord.HTTPException as e:
            return await ctx.send(f"{await author_ping(ctx)} Ban failed: {e}")

        # Modlog embed
        modlog = await get_channel(ctx.guild.id, "modlog")
        if modlog:
            embed = discord.Embed(color=discord.Color.red(), title="PURGE BAN")
            if getattr(user, "avatar", None):
                embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="User",   value=user.mention, inline=True)
            embed.add_field(name="Mod",    value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await modlog.send(embed=embed)

        await ctx.send(
            f"{await author_ping(ctx)} - {user.mention} was purge banned with all messages from the last 7 days deleted."
        )





    # !slowmode
    @commands.command(aliases=['slow'])
    async def slowmode(self, ctx, time: str = None):

        # No perms
        user_level = await get_level(ctx)
        if user_level < 1:
            return

        # Time not supplied
        if time is None:
            return await ctx.send(f"{await author_ping(ctx)} Please provide a time. ``!slowmode <time/off>``")

        # Turn slowmode off
        if time == "off":
            await ctx.channel.edit(slowmode_delay=0)
            await ctx.send(f"{await author_ping(ctx)} Slowmode turned off.")
            return

        # Time is an int, interpret as seconds
        if time.isdigit():
            time = int(time)
            if time > 21600:
                return await ctx.send(f"{await author_ping(ctx)} Rate too high! Must be below 21600 seconds (6 hours).")
            else:
                await ctx.channel.edit(slowmode_delay=time)
                await ctx.send(f"{await author_ping(ctx)} Slowmode set to {time} second(s).")
                return

        # Pattern match for s/d/h
        match = re.match(r"^(\d+)([smh])$", time.strip().lower())
        if not match:
            return await ctx.send(f"{await author_ping(ctx)} Invalid format. Use like ``!slowmode 10s``, ``5m``, or ``1h``.")
        
        value, unit = match.groups()
        value = int(value)

        if unit == 's':
            seconds = value
        elif unit == 'm':
            seconds = value * 60
        elif unit == 'h':
            seconds = value * 3600

        if seconds > 21600:
            return await ctx.send(f"{await author_ping(ctx)} Rate too high! Must be below 21600 seconds (6 hours).")

        # Do the thingy
        await ctx.channel.edit(slowmode_delay=seconds)

        # trim the .0
        if unit == 's':
            display = f"{value} second(s)"
        elif unit == 'm':
            display = f"{value} minute(s)"
        elif unit == 'h':
            display = f"{value} hour(s)"

        await ctx.send(f"{await author_ping(ctx)} Slowmode set to {display}.")





    # !mute
    @commands.command(aliases=['timeout'])
    async def mute(self, ctx, user_str: str = None, time: str = None, *, reason: typing.Optional[str] = None):

        # No perms
        user_level = await get_level(ctx)
        if user_level < 1:
            return

        if reason is None:
            reason = "None provided"

        # Args not supplied
        if user_str is None or time is None:
            return await ctx.send(f"{await author_ping(ctx)} Usage: ``!mute <user> <time/off> <reason>``")

        # Find user
        try:
            user = await commands.MemberConverter().convert(ctx, user_str)
        except commands.MemberNotFound:
            try:
                user = await commands.UserConverter().convert(ctx, user_str)
            except commands.UserNotFound:
                return await ctx.send(f"{await author_ping(ctx)} Couldn't find `{user_str}`")

        # Turn mute off
        if time == "off" or time == "0":
            await user.timeout_for(datetime.timedelta(seconds=0), reason="Unmuted")
            await ctx.send(f"{await author_ping(ctx)} {await user_ping(ctx, user)} unmuted.")
            return

        # Time is an int, interpret as seconds
        if time.isdigit():
            seconds = int(time)
            if seconds > 21600:
                return await ctx.send(f"{await author_ping(ctx)} Rate too high! Must be below 21600 seconds (6 hours).")
            else:
                duration = datetime.timedelta(seconds=seconds)
                display = f"{seconds} second(s)"
                await user.timeout_for(duration, reason=reason)
                await ctx.send(f"{await author_ping(ctx)} - {await user_ping(ctx, user)} timed out for {display}.")
                return

        # Pattern match for s/d/h
        match = re.match(r"^(\d+)([smh])$", time.strip().lower())
        if not match:
            return await ctx.send(f"{await author_ping(ctx)} Invalid format. Use like ``!mute <user> <time> (10s, 5m, 1h), <reason>``")
        
        value, unit = match.groups()
        value = int(value)

        if unit == 's':
            seconds = value
        elif unit == 'm':
            seconds = value * 60
        elif unit == 'h':
            seconds = value * 3600

        if seconds > 21600:
            return await ctx.send(f"{await author_ping(ctx)} Rate too high! Must be below 21600 seconds (6 hours).")

        # trim the .0
        if unit == 's':
            display = f"{value} second(s)"
        elif unit == 'm':
            display = f"{value} minute(s)"
        elif unit == 'h':
            display = f"{value} hour(s)"

        # Modlog embed
        modlog = await get_channel(ctx.guild.id, "modlog")
        if modlog:
            embed = discord.Embed(color=discord.Color.purple(), title="User Muted")
            if getattr(user, "avatar", None):
                embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="User",   value=user.mention,       inline=True)
            embed.add_field(name="Mod",    value=ctx.author.mention, inline=True)
            embed.add_field(name="Duration", value=display,          inline=False)
            embed.add_field(name="Reason", value=reason,             inline=False)
            await modlog.send(embed=embed)

        # Send the DM
        dm_status = ""
        if not user.bot:
            try:
                dm_embed = discord.Embed(
                    title=f"You were muted in {ctx.guild.name} for {display}",
                    color=discord.Color.purple(),
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

        # Do the thingy
        duration = datetime.timedelta(seconds=seconds)
        await user.timeout_for(duration, reason=reason)

        await ctx.send(f"{await author_ping(ctx)} - {await user_ping(ctx, user)} timed out for {display}.{dm_status}")
