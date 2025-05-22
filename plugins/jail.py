import discord, asyncio, datetime, io, zipfile
from datetime import timedelta
from typing import Optional
from discord.ext import commands
from discord.utils import get
from inc.utils import *

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):
    
    # Cogs
    bot.add_cog(JailCog(bot))




#################################################################################




#################################################################################
# Jail Cog
#################################################################################
class JailCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # !help info
        self.__help__ = {
            "jail": {
                "args": "<user(s)>",
                "desc": "Sends select user(s) to a private jail.",
                "perm": ["submod", "mod", "admin"]
            },
            "release": {
                "args": "<user(s)/all>",
                "desc": "Releases select user(s) from jail.",
                "perm": ["submod", "mod", "admin"]
            },
            "close": {
                "args": "",
                "desc": "Closes the jail and creates logs.",
                "perm": ["submod", "mod", "admin"]
            },
        }

    # Date formatting
    def format_date(self, date):
        suffix = ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"]
        day = date.day
        suffix_index = 0 if 10 <= day % 100 <= 20 else day % 10
        formatted_day = f"{day}{suffix[suffix_index]}"
        return date.strftime(f"%B {formatted_day}, %Y")




    # !jail command
    @commands.command()
    async def jail(self, ctx):

        # Drop out if no perms
        user_level = await get_level(ctx)
        if user_level < 1:
            return

        # Parse the users
        args = ctx.message.content.split()[1:]
        members = []

        for arg in args:
            if arg.startswith("<@") and arg.endswith(">"):
                user_id = arg.strip("<@!>")
            else:
                user_id = arg

            if user_id.isdigit():
                member = ctx.guild.get_member(int(user_id))
                if member:
                    members.append(member)

        if not members:
            await ctx.send(f"{ctx.author.mention} Please mention at least one valid user or user ID. `!jail @user1 1234567890 ...`")
            return

        # Get the roles
        roles = {}
        for row in db_read("roles", [f"guild_id:{ctx.guild.id}", "role:*"]):
            name, role_id = row[2], row[3]
            if role_id:
                roles[name] = int(role_id)

        jail_role_id = roles.get("jail")
        if not jail_role_id:
            return await ctx.send(f"{ctx.author.mention} This server's roles aren't configured properly.")

        jail_role = ctx.guild.get_role(jail_role_id)
        if not jail_role:
            return await ctx.send(f"{ctx.author.mention} Jail role is missing or misconfigured.")

        for member in members:
            if jail_role not in member.roles:
                await member.add_roles(jail_role)

        await ctx.send(f"{ctx.author.mention} sent {', '.join(m.mention for m in members)} to jail!")

        # Check for jail category
        jail_category = await get_channel(ctx.guild.id, "jail_category")
        if not jail_category:
            return await ctx.send(f"{ctx.author.mention} Jail category is missing or misconfigured.")

        # Add role & update perms
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True),
        }

        for member in members:
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        for role_name in ("submod", "mod", "admin", "bots"):
            role_id = roles.get(role_name)
            if role_id:
                role = ctx.guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        # We need a jail list database for the id
        if not table_exists("jail_list"):
            new_db("jail_list", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER")
            ])

        # Get the id
        jails = db_read("jail_list", [f"guild_id:{ctx.guild.id}"])
        jail_id = int(jails[-1][0]) + 1 if jails else 1        
        db_insert("jail_list", ["guild_id"], [f"{ctx.guild.id}"])

        base_name = f"-{jail_id}"
        channel_name = f"jail-{base_name}"

        # Make the channel
        try:
            jail_channel = await ctx.guild.create_text_channel(channel_name, category=jail_category, overwrites=overwrites)
        except discord.Forbidden as e:
            await ctx.send(f"Permissions broke: {e}")
            return
        except Exception as e:
            await ctx.send(f"Unexpected error: {e}")
            return

        mentions = ", ".join(m.mention for m in members)
        await jail_channel.send(f"{mentions}, you have been jailed. Please wait for a staff member.")

    # !add
    @commands.command()
    async def add(self, ctx, *args):

        # Drop out if no perms
        user_level = await get_level(ctx)
        if user_level < 1:
            return

        if not args:
            return await ctx.send(f"{ctx.author.mention} Usage: `!add <user1> <user2> ... [#jail-channel]`")

        # Get the jail roles
        roles = {
            row[2]: int(row[3])
            for row in db_read("roles", [f"guild_id:{ctx.guild.id}", "role:*"])
            if row[3]
        }

        jail_role_id = roles.get("jail")
        if not jail_role_id:
            return await ctx.send(f"{ctx.author.mention} Jail role is not configured.")
        
        jail_role = ctx.guild.get_role(jail_role_id)
        if not jail_role:
            return await ctx.send(f"{ctx.author.mention} Jail role is missing or misconfigured.")

        # Are we in or out of a jail?
        where = ""

        if args and args[-1].startswith("<#") and args[-1].endswith(">"):
            channel_id = int(args[-1][2:-1])
            target_channel = guild.get_channel(channel_id)
            user_args = args[:-1]
            where = "out"
        else:
            if ctx.channel.name.startswith("jail-"):
                target_channel = ctx.channel
                user_args = args
                where = "in"
            else:
                return await ctx.send(f"{ctx.author.mention} You must specify a jail channel mention if not used in a jail channel.")

        if not target_channel or not isinstance(target_channel, discord.TextChannel):
            return await ctx.send(f"{ctx.author.mention} Invalid jail channel.")

        # Parse the users
        members = []
        for arg in user_args:
            if arg.startswith("<@") and arg.endswith(">"):
                user_id = arg.strip("<@!>")
            else:
                user_id = arg
            if user_id.isdigit():
                member = ctx.guild.get_member(int(user_id))
                if member:
                    members.append(member)

        if not members:
            return await ctx.send(f"{ctx.author.mention} No valid users found.")

        # Add the roles
        for member in members:
            if jail_role not in member.roles:
                await member.add_roles(jail_role)

            await potential_channel.set_permissions(
                member,
                read_messages=True,
                send_messages=True,
                view_channel=True
            )

        # Confirmation
        mentions = ", ".join(m.mention for m in members)
        await target_channel.send(f"{ctx.author.mention} added {mentions} to {potential_channel.mention}")

        if where == "out":
            await ctx.send(f"{ctx.author.mention} Done.")

    # !release command
    @commands.command(name="release")
    async def release(self, ctx, *args):

        # Drop out if no perms
        user_level = await get_level(ctx)
        if user_level < 1:
            return

        guild = ctx.guild

        # Get the roles
        roles = {
            row[2]: int(row[3])
            for row in db_read("roles", [f"guild_id:{guild.id}", "role:*"])
            if row[3]
        }

        jail_role_id = roles.get("jail")
        if not jail_role_id:
            return await ctx.send(f"{ctx.author.mention} Jail role is not configured.")
        
        jail_role = guild.get_role(jail_role_id)
        if not jail_role:
            return await ctx.send(f"{ctx.author.mention} Jail role is missing or misconfigured.")

        # Are we in our out of a jail?
        where = ""
        if args and args[-1].startswith("<#") and args[-1].endswith(">"):
            channel_id = int(args[-1][2:-1])
            target_channel = guild.get_channel(channel_id)
            user_args = args[:-1]
            where = "out"
        else:
            if ctx.channel.name.startswith("jail-"):
                target_channel = ctx.channel
                user_args = args
                where = "in"
            else:
                return await ctx.send(f"{ctx.author.mention} You must use this in a jail channel or provide a jail channel mention.")

        if not target_channel or not isinstance(target_channel, discord.TextChannel):
            return await ctx.send(f"{ctx.author.mention} Invalid jail channel.")

        # Parse the users
        if len(user_args) == 1 and user_args[0].lower() == "all":
            members_to_release = [m for m in target_channel.members if jail_role in m.roles]
        else:
            members_to_release = []
            for user_str in user_args:
                try:
                    member = await commands.MemberConverter().convert(ctx, user_str)
                    if member:
                        members_to_release.append(member)
                except commands.BadArgument:
                    continue

        if not members_to_release:
            return await ctx.send(f"{ctx.author.mention} No valid users to release.")

        # Release the users
        for member in members_to_release:
            if jail_role in member.roles:
                await target_channel.set_permissions(member, overwrite=discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                    view_channel=False
                ))
                await member.remove_roles(jail_role)

        mentions = ", ".join(m.mention for m in members_to_release)
        await target_channel.send(f"{ctx.author.mention} released {mentions} from jail.")

        if where == "out":
            await ctx.send(f"{ctx.author.mention} Done.")

    # !close command
    @commands.command()
    async def close(self, ctx, *args):

        # Drop out if no perms
        user_level = await get_level(ctx)
        if user_level < 1:
            return

        guild = ctx.guild

        # Get the roles for the jail
        roles = {
            row[2]: int(row[3])
            for row in db_read("roles", [f"guild_id:{guild.id}", "role:*"])
            if row[3]
        }
        jail_role_id = roles.get("jail")
        if not jail_role_id:
            return await ctx.send(f"{ctx.author.mention} This server's roles aren't configured properly.")
        
        jail_role = guild.get_role(jail_role_id)
        if not jail_role:
            return await ctx.send(f"{ctx.author.mention} The jail role doesn't exist.")

        # Are we in our out of a jail?
        where = ""
        if args and args[-1].startswith("<#") and args[-1].endswith(">"):
            channel_id = int(args[-1][2:-1])
            target_channel = guild.get_channel(channel_id)
            where = "out"
        else:
            if ctx.channel.name.startswith("jail-"):
                target_channel = ctx.channel
                where = "in"
            else:
                return await ctx.send(f"{ctx.author.mention} You must use this in a jail channel or specify one with a channel mention.")

        if not target_channel or not target_channel.name.startswith("jail-"):
            return await ctx.send(f"{ctx.author.mention} That is not a valid jail channel.")

        # Find users to release
        members_to_release = [m for m in target_channel.members if jail_role in m.roles]
        for member in members_to_release:
            await member.remove_roles(jail_role)
            await target_channel.send(f"{ctx.author.mention} released {member.mention} from jail.")

        # Close the channel
        await target_channel.send("Wrapping up... This might take a minute if there were a lot of messages.")

        remaining = [m for m in target_channel.members if jail_role in m.roles]
        if remaining:
            return await ctx.send(f"{ctx.author.mention} Some members are still jailed. Aborting deletion.")

        # Get all the messages
        messages = await ctx.channel.history(limit=None, oldest_first=True).flatten()
        log_lines = []
        attachments = []

        # Gather all the messages and attachments
        for msg in messages:
            timestamp = self.format_date(msg.created_at)
            author = str(msg.author)
            content = msg.content.strip()

            if content:
                log_lines.append(f"{timestamp} - {author}: {content}")
            for embed in msg.embeds:
                log_lines.append(f"{timestamp} - {author} [sent an embed]")
            for attachment in msg.attachments:
                unique_name = f"{msg.id}_{attachment.filename}"
                attachments.append((unique_name, await attachment.read()))
                log_lines.append(f"{timestamp} - {author} [sent an attatchment]")

        # Create the log text file
        log_text = "\n".join(log_lines)
        log_file = discord.File(fp=io.BytesIO(log_text.encode()), filename=f"{target_channel.name}.txt")

        # Zip the attachments
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, data in attachments:
                zip_file.writestr(filename, data)
        zip_buffer.seek(0)

        zip_discord_file = discord.File(zip_buffer, filename=f"{target_channel.name}_attachments.zip")

        # Post the log
        log_channel = await get_channel(ctx.guild.id, "jaillog")
        if log_channel:
            await log_channel.send(f"Jail log from {target_channel.name}:", file=log_file)
            if attachments:
                await log_channel.send(f"All attachments from {target_channel.name}:", file=zip_discord_file)

        # Baleet channel
        await target_channel.delete()

        if where == "out":
            await ctx.send(f"{ctx.author.mention} Done.")