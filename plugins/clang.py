import random
from discord.ext import commands

class ClangCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Help info
        self.__help__ = {
            "clang": {
                "args": "",
                "desc": "Make Clang say stuff",
                "perm": "everyone"
            }
        }

    @commands.command()
    async def clang(self, ctx):
        # Generate a random number between 1 and 5
        choice = random.randint(1, 21)

        # Define a dictionary that maps numbers to messages
        messages = {
            1: "aaaaaaaaaAAAAAAAAAAAAAAAA",
            2: "I AM CLANG. THE FLESH ROTS BUT THE SOUL PERSISTS.",
            3: "In the depths they call me a behemoth, and to the seas I am leviathan. Hell rides in my wake.",
            4: "CLANG 👏  CLANG 👏  CLANG 👏",
            5: "clang",
            6: "who's clang",
            7: "FEED ME SPAGHETTI CLANG DEMANDS SPPGEAGEAHGFJ",
            8: "-# aaaaaa sneaky clang",
            9: "Are you okay Clang? Clang once for yes, twice for no.",
            10: "WHAT'S THE WIFI PASSWORD???? CLANG NEED WIFI.",
            11: "If you stay here too long, you'll end up frying your brain.",
            12: "???AAAAAAA???",
            13: "STAY HYDRATED WITH THE BLOOD OF YOUR ENEMIES",
            14: "NO MORE !CLANG AAAAAAAAA",
            15: "I'd just like to interject for a moment. What you're referring to as Clang is infact, SKULL/Clang, or as I've recently taken to calling it, SKULL PLUS CLANG.",
            16: "bleeeehhhh *ding*",
            17: "splunk",
            18: "!clang command kinda clunchy ngl",
            19: "I AM CLAG I MEAN CLANG",
            20: "clang reference",
            21: "THE CLOCKS ARE LYING TO YOU, IT'S ALWAYS 3:07 PM."
        }

        # Get the message corresponding to the chosen number
        await ctx.send(messages.get(choice))

# This setup function adds the cog to the bot
def setup(bot):
    bot.add_cog(ClangCog(bot))
