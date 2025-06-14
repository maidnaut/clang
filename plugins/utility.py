import discord, os, asyncio, argparse
from datetime import datetime
from discord.ext import commands
from inc.utils import *

#################################################################################
# Init
#################################################################################

def setup(bot):

    # Cogs
    bot.add_cog(UtilsCog(bot))




#################################################################################




#################################################################################
# Utils
#################################################################################
class UtilsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # !help info
        self.__help__ = {
            "whois": {
                "args": "<user:optional>",
                "desc": "Displays user data",
                "perm": "everyone"
            },
            "ping": {
                "args": "",
                "desc": "Check Clang's latency",
                "perm": "everyone"
            },
            "avatar": {
                "args": "<user:optional>",
                "desc": "Displays an avatar",
                "perm": "everyone"
            },
            "serverinfo": {
                "args": "",
                "desc": "Displays server data",
                "perm": "everyone"
            },
            "source": {
                "args": "",
                "desc": "Github url",
                "perm": "everyone"
            },
            "privacy": {
                "args": "",
                "desc": "Shows Clang's privacy policy.",
                "perm": "everyone"
            }
        }

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



#################################################################################
# !privacy
#################################################################################

    @commands.command()
    async def privacy(self, ctx):
        embed = discord.Embed(
            title="Privacy Policy",
            description="Here’s what Clang stores and how your data is handled.",
            color=discord.Color.blue()
        )

        embed.add_field(name="", value="\n\n", inline=False)

        embed.add_field(
            name="Stored Data",
            value=(
                "- **User Notes**: Optional. Notes you create are stored with your user ID. "
                "You can delete them at any time with `!dn <id>`.\n"
                "- **Cookies**: Stores user ID + cookie count per server.\n"
                "- **Moderation Logs**: If enabled by server mods, bans/warns/etc are logged to a modlog channel.\n"
                "- **Guild Configs**: Stores channel/role IDs and plugin settings for bot functionality.\n"
                "- **Markov Chains**: Learns from messages in enabled channels. Does **not** store author IDs or message metadata. Markov data is anonymized and chunked into 3 word lengths.\n"
                "- Server admins can disable any feature or clear data at any time."
            ),
            inline=False
        )

        embed.add_field(name="", value="\n\n", inline=False)

        embed.add_field(
            name="What Clang doesn't store",
            value=(
                "- No message logs\n"
                "- No DMs\n"
                "- No cross-server tracking\n"
                "- No analytics or usage tracking"
            ),
            inline=False
        )

        embed.add_field(name="", value="\n\n", inline=False)

        embed.add_field(
            name="Your Controls",
            value=(
                "- `!dn <id>` - delete your notes\n"
                "- `!markov optout` *(coming soon)* - exclude your messages from training\n"
                "- Server admins can enable/disable any plugin via config"
            ),
            inline=False
        )

        return await ctx.send(embed=embed)





#################################################################################
# !source
#################################################################################

    @commands.command()
    async def source(self, ctx):
        return await ctx.send("https://github.com/maidnaut/clang")





#################################################################################
# !whois
#################################################################################

    @commands.command()
    async def whois(self, ctx, *, user_input: str = None):
        author = ctx.author

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
            await ctx.send(f"{await author_ping(ctx)} I have no record for that user.")
            return

        # Run the whois
        member = ctx.guild.get_member(user.id) or user
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

        # Do whois embed + warnings
        warnings = db_read("warnings", [f"guild_id:{ctx.guild.id}", f"user_id:{user.id}"])

        await ctx.send(embed=embed)

        warnings_text = f"{member.mention if isinstance(member, discord.Member) else user.mention}'s Warnings:\n"

        if not warnings:
            warnings_text += "No warnings found for this user."

            await ctx.send(warnings_text)

            return

        for i, result in enumerate(warnings, start=1):
            note_id = result[3]
            user_id = result[2]
            full_date = result[6]
            author_id = result[5]
            reason = result[4]

            dt = datetime.fromisoformat(full_date)
            date = dt.strftime("%B %d, %Y")

            warnings_text += f"**{note_id})** {date}, by {await check_ping_id(ctx, str(author_id))}  — {reason}\n"

        await ctx.send(warnings_text.strip())




#################################################################################
# !ping
#################################################################################

    @commands.command()
    async def ping(self, ctx):
        latency_ms = round(self.bot.latency * 1000, 2)
        await ctx.send(f"{await author_ping(ctx)} Pong! `{latency_ms}ms`")

#################################################################################
# !serverinfo
#################################################################################

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
        embed.add_field(name="Creation", value=f"{guild.created_at.strftime('%b %d %Y')} - ", inline=True)
        embed.add_field(name="Members", value=f"{guild.member_count}", inline=True)
        await ctx.send(embed=embed)

#################################################################################
# !avatar
#################################################################################
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
            await ctx.send(f"{await author_ping(ctx)} I have no record for that user.")
            return

        embed = discord.Embed(
            color=discord.Color.blurple(),
            description=f"{await user_ping(ctx, user)} (`{user.name}`)"
        )

        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
