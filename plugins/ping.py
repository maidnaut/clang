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
