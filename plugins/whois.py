import discord
import os
import sqlite3
import asyncio
import random
from discord.ext import commands
from db import db_create, db_read, db_update

# Elevated permission roles
ALUMNI_ROLE = int(os.getenv("alumniRole"))
MODERATOR_ROLE = int(os.getenv("moderatorRole"))
ADMIN_ROLE = int(os.getenv("adminRole"))
OPERATOR_ROLE = int(os.getenv("operatorRole"))
ROOT_ROLE = int(os.getenv("rootRole"))

class WhoisCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whois(self, ctx, *, user_input: str = None):
        author = ctx.author

        if user_input is None:
            await ctx.send("You must supply a target. ``!whois <@user/id>``")
            return
        
        user = None

        # First, check if there's a mention
        if ctx.message.mentions:
            user = ctx.message.mentions[0]

        # Second, if it's all digits, try to fetch by user ID
        elif user_input.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_input))
                member = ctx.guild.get_member(user.id)  # Check if they're in the guild
                if member:
                    user = member
            except discord.NotFound:
                user = None
            except discord.HTTPException:
                user = None

        if user is None:
            await ctx.send(f"I have no record for that user.")
            return
        
        # Permission check
        author_roles = [role.id for role in author.roles]
        elevated_roles = (ALUMNI_ROLE, MODERATOR_ROLE, OPERATOR_ROLE, ADMIN_ROLE, ROOT_ROLE)

        # Initial embed setup
        member = ctx.guild.get_member(user.id) or user  # Use member if possible
        display_name = ""
        join_date = member.joined_at.strftime("%Y-%m-%d") if isinstance(member, discord.Member) and member.joined_at else "N/A"
        created_at = user.created_at.strftime("%Y-%m-%d")

        embed = discord.Embed(
            color=discord.Color.blurple(),
            description=f"**{member.mention if isinstance(member, discord.Member) else user.mention}** (`{user.name}`)"
        )
        embed.set_author(name=display_name, icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Account Created", value=f"{created_at} ", inline=True)
        embed.add_field(name="Joined Server", value=f"{join_date}", inline=True)
        embed.add_field(name="", value=f"ID: `{user.id}`", inline=False)

        if any(role in author_roles for role in elevated_roles):

            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()

            c.execute('SELECT * FROM warnings WHERE user_id = ?', (user.id,))
            results = c.fetchall()

            conn.close()

            await ctx.send(embed=embed)

            warnings_text = "**Warnings**\n\n"
            embed2 = discord.Embed(
                color=discord.Color.blurple(),
                description=f"Warnings"
            )

            if not results:  # correct check for an empty list
                embed = discord.Embed(
                    color=discord.Color.blurple(),
                )
                embed.add_field(name="", value="No warnings found for this user.", inline=True)

                await ctx.send(embed=embed)

                return

            for i, result in enumerate(results, start=1):
                note_id = result[1]
                user_id = result[2]
                full_date = result[3]
                author_id = result[4]
                reason = result[5]

                date = full_date.split(" ")[0]

                warnings_text += f"**{note_id})** by <@{author_id}> on {date}  — {reason}\n"

            embed2.description = warnings_text.strip()
            await ctx.send(embed=embed2)

        else:
            await ctx.send(embed=embed)
            return

def setup(bot):
    bot.add_cog(WhoisCog(bot))
