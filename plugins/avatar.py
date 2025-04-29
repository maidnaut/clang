import discord
from discord.ext import commands

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
