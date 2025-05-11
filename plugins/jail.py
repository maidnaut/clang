import discord, asyncio, datetime, io
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

    # jaillog channel
    async def get_jaillog_channel(self, ctx):
        try:
            guild_id = ctx.guild.id
            settings = db_read("logchans", [f"guild_id:{guild_id}", f"name:jaillog"])
            if not settings or not settings[0][3]:
                return None
            
            channel_id = int(settings[0][3])
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                try:
                    channel = await guild.fetch_channel(channel_id)
                except discord.NotFound:
                    await ctx.send(f"Jaillog channel {channel_id} not found in guild {guild_id}")
                    return None
            
            return channel
        except Exception as e:
            await ctx.send(f"Error getting jaillog channel: {e}")
            return None

    # jaillog channel
    async def get_jail_category(self, ctx):
        try:
            guild_id = ctx.guild.id
            settings = db_read("logchans", [f"guild_id:{guild_id}", f"name:jail_category"])
            if not settings or not settings[0][3]:
                return None
            
            channel_id = int(settings[0][3])
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                try:
                    channel = await guild.fetch_channel(channel_id)
                except discord.NotFound:
                    await ctx.send(f"Jail category {channel_id} not found in guild {guild_id}")
                    return None
            
            return channel
        except Exception as e:
            await ctx.send(f"Error getting jail category: {e}")
            return None




    # !jail command
    @commands.command()
    async def jail(self, ctx):

        user_level = await get_level(ctx)
        if user_level < 1:
            return

        members = ctx.message.mentions
        if not members:
            await ctx.send(f"{ctx.author.mention} Please mention at least one user. `!jail @user1 @user2 ...`")
            return

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

        jail_category = await self.get_jail_category(ctx)
        if not jail_category:
            return await ctx.send(f"{ctx.author.mention} Jail category is missing or misconfigured.")

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


        if not table_exists("jail_list"):
            new_db("jail_list", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER")
            ])

        jails = db_read("jail_list", [f"guild_id:{ctx.guild.id}"])
        jail_id = int(jails[-1][0]) + 1 if jails else 1        
        db_insert("jail_list", ["guild_id"], [f"{ctx.guild.id}"])

        base_name = f"-{jail_id}"
        channel_name = f"jail-{base_name}"

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

    # !release command
    @commands.command(name="release")
    async def release(self, ctx, *args):

        if not ctx.channel.name.startswith("jail-"):
            return await ctx.send(f"{ctx.author.mention} `!release all` can only be used in a jail channel.")

        user_level = await get_level(ctx)
        if user_level < 1:
            return

        guild = ctx.guild

        roles = {row[2]: int(row[3]) for row in db_read("roles", [f"guild_id:{guild.id}", "role:*"]) if row[3]}
        jail_role_id = roles.get("jail")
        if not jail_role_id:
            return await ctx.send(f"{ctx.author.mention} This server's roles aren't configured properly.")
        
        jail_role = guild.get_role(jail_role_id)
        if not jail_role:
            return await ctx.send(f"{ctx.author.mention} The jail role doesn't exist.")

        members_to_release = []

        if len(args) == 1 and args[0].lower() == "all":
            members_to_release = [m for m in ctx.channel.members if jail_role in m.roles]
        else:
            for user_str in args:
                member = await commands.MemberConverter().convert(ctx, user_str)
                members_to_release.append(member)

        if not members_to_release:
            return await ctx.send(f"{ctx.author.mention} Please provide users to release. `!release <user(s)/all>")

        for member in members_to_release:
            if jail_role in member.roles:

                overwrite = discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                    view_channel=False
                )

                await ctx.channel.set_permissions(member, overwrite=overwrite)
                await member.remove_roles(jail_role)

                await ctx.send(f"{ctx.author.mention} released {member.mention} from jail.")

    # !close command
    @commands.command(name="close")
    async def close(self, ctx):
        
        if ctx.channel.name.startswith("jail-"):

            user_level = await get_level(ctx)
            if user_level < 1:
                return

            guild = ctx.guild

            roles = {row[2]: int(row[3]) for row in db_read("roles", [f"guild_id:{guild.id}", "role:*"]) if row[3]}
            jail_role_id = roles.get("jail")
            if not jail_role_id:
                return await ctx.send(f"{ctx.author.mention} This server's roles aren't configured properly.")
            
            jail_role = guild.get_role(jail_role_id)
            if not jail_role:
                return await ctx.send(f"{ctx.author.mention} The jail role doesn't exist.")
            
            members_to_release = [m for m in ctx.channel.members if jail_role in m.roles]

            if members_to_release:
                for member in members_to_release:
                    if jail_role in member.roles:
                        await member.remove_roles(jail_role)
                        await ctx.send(f"{ctx.author.mention} released {member.mention} from jail.")

            await ctx.send("Wrapping up... This might take a minute of there were a lot of messages.")

            remaining = [m for m in ctx.channel.members if jail_role in m.roles]
            
            if not remaining:

                messages = await ctx.channel.history(limit=None, oldest_first=True).flatten()
                log_lines = []
                attachments = []

                for msg in messages:
                    timestamp = self.format_date(msg.created_at)
                    author = str(msg.author)
                    content = msg.content.strip()

                    if content:
                        log_lines.append(f"{timestamp} - {author}: {content}")

                    for embed in msg.embeds:
                        log_lines.append(f"{timestamp} - {author} sent an embed: [embed not included in text log]")

                    for attachment in msg.attachments:
                        attachments.append(attachment)

                log_lines = [f"{self.format_date(msg.created_at)} - {msg.author}: {msg.content}" for msg in messages]
                log_text = "\n".join(log_lines)

                log_file = discord.File(fp=io.BytesIO(log_text.encode()), filename=f"{ctx.channel.name}.txt")

                log_channel = await self.get_jaillog_channel(ctx)
                if log_channel:
                    await log_channel.send(f"Jail log from {ctx.channel.name}:", file=log_file)

                    for attachment in attachments:
                        await log_channel.send(f"Attachment from {ctx.channel.name}:", file=await attachment.to_file())

                await ctx.channel.delete()


