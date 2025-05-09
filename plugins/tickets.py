import discord, asyncio, datetime, io
from datetime import timedelta
from typing import Optional
from discord.ext import commands
from discord.utils import get
from inc.utils import *

ticket = discord.SlashCommandGroup("ticket", "Ticket related commands")

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):
    
    # Cogs
    bot.add_cog(TicketsCog(bot))




#################################################################################




#################################################################################
# Tickets Cog
#################################################################################
class TicketsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.add_application_command(ticket)

    def level_required(min_level: int):
        async def level_check(ctx):
            return await get_level(ctx) >= min_level
        return commands.check(level_check)

    def format_date(self, date):
        suffix = ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"]
        day = date.day
        suffix_index = 0 if 10 <= day % 100 <= 20 else day % 10
        formatted_day = f"{day}{suffix[suffix_index]}"
        return date.strftime(f"%B {formatted_day}, %Y")
        
    # ticketlog channel
    async def get_ticketlog_channel(self, ctx):
        try:
            guild_id = ctx.guild.id
            settings = db_read("logchans", [f"guild_id:{guild_id}", f"name:ticketlog"])
            if not settings or not settings[0][3]:
                return None
            
            channel_id = int(settings[0][3])
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                try:
                    channel = await guild.fetch_channel(channel_id)
                except discord.NotFound:
                    await ctx.send(f"Ticketlog channel {channel_id} not found in guild {guild_id}")
                    return None
            
            return channel
        except Exception as e:
            await ctx.send(f"Error getting ticketlog channel: {e}")
            return None
        
    # tickets category
    async def get_ticket_category(self, ctx):
        try:
            guild_id = ctx.guild.id
            settings = db_read("logchans", [f"guild_id:{guild_id}", f"name:ticket_category"])
            if not settings or not settings[0][3]:
                return None
            
            channel_id = int(settings[0][3])
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                try:
                    channel = await guild.fetch_channel(channel_id)
                except discord.NotFound:
                    await ctx.send(f"Ticket category {channel_id} not found in guild {guild_id}")
                    return None
            
            return channel
        except Exception as e:
            await ctx.send(f"Error getting ticket category: {e}")
            return None




    # /ticket open
    @ticket.command(name="open", description="Open a new ticket")
    async def open_ticket(ctx, title: str):

        await ctx.respond("Ticket created.", ephemeral=True)
        cog: TicketsCog = ctx.bot.get_cog("TicketsCog")

        tickets_category = await cog.get_ticket_category(ctx)
        if not tickets_category:
            return await ctx.respond(f"{ctx.author.mention} Ticket category is missing or misconfigured.")

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
        }

        roles = {}
        for row in db_read("roles", [f"guild_id:{ctx.guild.id}", "role:*"]):
            name, role_id = row[2], row[3]
            if role_id:
                roles[name] = int(role_id)

        for role_name in ("submod", "mod", "admin", "bots"):
            role_id = roles.get(role_name)
            if role_id:
                role = ctx.guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True)


        if not table_exists("ticket_list"):
            new_db("ticket_list", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER")
            ])

        tickets = db_read("ticket_list", [f"guild_id:{ctx.guild.id}"])
        ticket_id = int(tickets[-1][0]) + 1 if tickets else 1        
        db_insert("ticket_list", ["guild_id"], [f"{ctx.guild.id}"])

        base_name = f"-{ticket_id}"
        channel_name = f"ticket-{base_name}"
        ticket_channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, category=tickets_category)

        mod_role = discord.utils.get(ctx.guild.roles, name="mods")
        mod_mention = mod_role.mention if mod_role else "@mods"

        await ticket_channel.send(f"""
**Title: {title}**

Hello {ctx.author.mention}, please be patient and wait for the {mod_mention}.

Please also provide message links, screenshots, and any context you think is relevant. Mods will cose the ticket when the isue is resolved, thank you!

Use `/ticket add <user>` to add someone else to the ticket.
""")




    # /ticket add
    @ticket.command(name="add", description="Add a user to the ticket")
    async def add_user(ctx, user: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.respond("This command can only be used inside a ticket channel.", ephemeral=True)

        overwrite = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            view_channel=True
        )

        await ctx.channel.set_permissions(user, overwrite=overwrite)
        await ctx.respond(f"{user.mention} has been added to the ticket.")




    # /ticket remove
    @ticket.command(name="remove", description="Remove a user from the ticket")
    @level_required(1)
    async def add_user(ctx, user: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.respond("This command can only be used inside a ticket channel.", ephemeral=True)

        user_level = await get_level(ctx)
        if user_level < 1:
            return await ctx.respond("You don't have permission to remove users from a ticket.", ephemeral=True)
            return

        overwrite = discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
            view_channel=False
        )

        await ctx.channel.set_permissions(user, overwrite=overwrite)
        await ctx.respond(f"{user.mention} has been removed from the ticket.")




    # /ticket close
    @ticket.command(name="close", description="Close the ticket")
    @level_required(1)
    async def close_ticket(ctx):
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.respond("This command can only be used inside a ticket channel.", ephemeral=True)

        user_level = await get_level(ctx)
        if user_level < 1:
            return await ctx.respond("You don't have permission to close a ticket.", ephemeral=True)

        await ctx.respond("Closing ticket.", ephemeral=True)
        cog: TicketsCog = ctx.bot.get_cog("TicketsCog")

        await ctx.send("Wrapping up... This might take a minute if there were a lot of messages.")

        messages = await ctx.channel.history(limit=None, oldest_first=True).flatten()
        log_lines = []
        attachments = []

        for msg in messages:
            timestamp = cog.format_date(msg.created_at)
            author = str(msg.author)
            content = msg.content.strip()

            if content:
                log_lines.append(f"{timestamp} - {author}: {content}")

            for embed in msg.embeds:
                log_lines.append(f"{timestamp} - {author} sent an embed: [embed not included in text log]")

            for attachment in msg.attachments:
                attachments.append(attachment)

        log_text = "\n".join(log_lines)
        log_file = discord.File(fp=io.BytesIO(log_text.encode()), filename=f"{ctx.channel.name}.txt")

        log_channel = await cog.get_ticketlog_channel(ctx)
        if log_channel:
            await log_channel.send(f"Ticket log from {ctx.channel.name}:", file=log_file)

            for attachment in attachments:
                await log_channel.send(f"Attachment from {ctx.channel.name}:", file=await attachment.to_file())

        await ctx.channel.delete()


