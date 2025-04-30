import discord
import os
import asyncio
from discord.ext import commands

class PingCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Help info
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

def setup(bot):
    bot.add_cog(PingCog(bot))

class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Help info
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

def setup(bot):
    bot.add_cog(ServerInfoCog(bot))

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Help info
        self.__help__ = {
            "avatar": {
                "args": "<user:optional>",
                "desc": "Displays an avatar",
                "perm": "everyone"
            }
        }

    @commands.command()
    async def avatar(self, ctx, *, user_input: str = None):
        # Default to the command author's avatar if no user input is given
        if user_input is None:
            user = ctx.author
        else:
            if ctx.message.mentions:
                # If the user is mentioned, use the first mentioned user
                user = ctx.message.mentions[0]
            elif user_input.isdigit():
                # Try to fetch the user by ID if user_input is a digit
                try:
                    user = await self.bot.fetch_user(int(user_input))
                    member = ctx.guild.get_member(user.id)  # Check if they're in the guild
                    if member:
                        user = member  # Use the member object if they are in the guild
                except discord.NotFound:
                    user = None
                except discord.HTTPException:
                    user = None
            else:
                user = None

        # If no user is found, send a message and return
        if user is None:
            await ctx.send(f"I have no record for that user.")
            return

        # If a valid user was found, create the embed and send it
        embed = discord.Embed(
            color=discord.Color.blurple(),
            description=f"**{user.mention}** (`{user.name}`)"
        )

        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(AvatarCog(bot))