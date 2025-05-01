import discord, os, asyncio, argparse, random
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *

# Fun commands: !clang !clnag !fortune !flip !roll

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):
    
    init_term()

    # Cogs
    bot.add_cog(ClangCog(bot))
    bot.add_cog(ClnagCog(bot))
    bot.add_cog(FortuneCog(bot))




#################################################################################




#################################################################################
# !clang command
#################################################################################

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

#################################################################################
# !clnag command
#################################################################################

class ClnagCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clnag(self, ctx):
        user = ctx.author

        await ctx.send(f"haha {user.name} said clnag")

#################################################################################
# !fortune command
#################################################################################

words = ["pluh", "splunk", "clunch", "spuss", "fleck", "bluck", "submitially", "legume", "gluent", "gnome", "rat", "sympatico", "speculus", "effluvia", "tempest", "ariona", "borealis", "ruck", "bogden", "ash", "briar", "blint", "clang"]
concepts = [
    "static", "teeth", "whispers", "fractals", "mold",  
    "glass", "the void", "laughter", "rot", "nails",  
    "moths", "blood", "milk", "salt", "ash",  
    "dust", "echoes", "worms", "ink", "rust",  
    "smoke", "amber", "veins", "honey", "lichen",  
    "a shadow", "a glitch", "thorns", "piss", "moonlight",
    "guilt", "chaos", "ignorance", "hate"
]

animals = [
    "trash panda",
    "rabbid possum",
    "schizophrenic crow",
    "tumor",
    "hairless cat",  
    "bear that eats garbage",
    "blobfish",
    "pile of asbestos",
    "trash can",
    "reverse-mermaid",
    "rat king",
    "fox that's actually three foxes in a trench coat",
    "plastic bag (it's thriving)",
    "moldy piece of bread",
    "dust bunny",
    "frog",
    "handful of pocket lint",
]

class FortuneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Help info
        self.__help__ = {
            "fortune": {
                "args": "",
                "desc": "Get a fortune from Clang",
                "perm": "everyone"
            }
        }

    @commands.command()
    async def fortune(self, ctx):
        # Generate a random number between 1 and 5
        choice = random.randint(1, 21)

        word = random.choice(words)
        concept = random.choice(concepts)
        animal = random.choice(animals)

        # Define a dictionary that maps numbers to messages
        messages = {
            1: "Your shadow has been gossiping about you.",
            2: "Something is looking back at you in the mirror. Wait, that's you.",
            3: f"Tomorrow’s soup will taste like the concept of {concept}. Don't eat it. Do you eat soup or drink it?",
            4: "Your left shoe is plotting something. Right shoe is in on it.",
            5: "Give Clang your cookies, and your fortunes will always be true.",
            6: "Your teeth are whispering secrets. If you listen closely, you can hear them.",
            7: "The air tastes purple today. Inhale cautiously.",
            8: "Your next sneeze will summon something. Apologize in advance.",
            9: "Your shadow has been seen in places you haven’t.",
            10: "The static is a language. Learn it.",
            11: "Your patience will be rewarded—just not in the way you expect.",
            12: "A friend will ask for your advice. They won’t take it.",
            13: "A small gnome in your mind is flipping coins to decide your fate. It’s rigged.",
            14: "You are the golden apple. Also, you are the worm inside it.",
            15: "A mysterious stranger will give you a suspiciously heavy envelope. (It’s just rocks.)",
            16: f"Your spirit animal is a {animal}. Embrace this.",
            17: "The system is a hoax. The hoax is also a hoax.",
            18: "The voices in your head are forming a union. They demand better benefits.",
            19: f"A random word will soon become very important to you. Today’s word: '{word}'",
            20: "fortun bronk pls try again",
            21: "If you wanna win big, always bet on Clang."
        }

        # Get the message corresponding to the chosen number
        await ctx.send(messages.get(choice))

#################################################################################




#################################################################################
# Register terminal stuff
#################################################################################
def init_term():

    # Init some text we'll use later
    command_name = "fun"

    usage = f"{command_name} [-args] [guild_id:optional]"
    
    example = """
    Usage example goes here
    """

    def function(args: list[str]):

        # Put the terminal response function here
        print("todo")
 

    # Help page & register
    register_plugin(
        name=command_name,
        help=f"""
template: {usage}
    Put the description here

    Options:
        --args           Explanation of arg

    Extra information here

    Usage:
{example}


""",
        func=function
    )