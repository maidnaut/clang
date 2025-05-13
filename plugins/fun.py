import discord, os, asyncio, argparse, random
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *

# Fun commands: !clang !clnag !fortune !flip !roll

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):

    # Cogs
    bot.add_cog(FunCog(bot))




class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Help info
        self.__help__ = {
            "clang": {
                "args": "",
                "desc": "Make Clang say stuff",
                "perm": "everyone"
            },
            "fortune": {
                "args": "",
                "desc": "Get a fortune from Clang",
                "perm": "everyone"
            },
            "flip": {
                "args": "",
                "desc": "Flip a coin (heads or tails)",
                "perm": "everyone"
            },
            "roll": {
                "args": "<#d#>",
                "desc": "Roll x number of dice with x sides (e.g. 2d6)",
                "perm": "everyone"
            },
        }




    # !clang
    @commands.command()
    async def clang(self, ctx):
        # Generate a random number for the response
        choice = random.randint(1, 25)

        # Response dict
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
            21: "THE CLOCKS ARE LYING TO YOU, IT'S ALWAYS 3:07 PM.",
            22: "I AM FLBAGNG THE FLEBSH ROPS BUT THE SKOUL REMAIBS MMPMPHPHPNMPMPMP",
            23: "ah, crumbs.",
            24: "i use arch btw",
            25: "install gentoo",
        }

        # Get the message corresponding to the chosen number
        await ctx.send(messages.get(choice))




    # !clnag
    @commands.command()
    async def clnag(self, ctx):
        user = ctx.author

        await ctx.send(f"haha {user.name} said clnag")
    



    # !fortune
    @commands.command()
    async def fortune(self, ctx):
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

        # Generate a random number for the response
        choice = random.randint(1, 24)

        word = random.choice(words)
        concept = random.choice(concepts)
        animal = random.choice(animals)

        # Response dict
        messages = {
            1: "Your shadow has been gossiping about you.",
            2: "Something is looking back at you in the mirror. Wait, that's you.",
            3: f"Tomorrow’s soup will taste like the concept of {concept}. Don't eat it. Do you eat soup or drink it? Probably best not to drink it either.",
            4: "Your left shoe is plotting something. Right shoe is in on it.",
            5: "Give Clang your cookies, and your fortunes will always be true.",
            6: "Your teeth are whispering secrets. If you listen closely, you can hear them.",
            7: "The air tastes purple today. Inhale cautiously.",
            8: "Your next sneeze will summon something. Apologies in advance.",
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
            21: "If you wanna win big, always bet on Clang.",
            22: "TOO MANY EXCESS VACATION DAYS? TAKE A GODDAMN VACATION STRAIGHT TO HELL",
            23: "NOW'S YOUR CHANCE TO BE A [[BIGSHOT]]",
            24: "[[HYPERLINK BLOCKED]]"
        }

        # Get the message corresponding to the chosen number
        await ctx.send(messages.get(choice))




    # !flip
    @commands.command()
    async def flip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"{ctx.author.mention} **{result}**!")




    # !roll
    @commands.command()
    async def roll(self, ctx, dice: str = None):

        if dice == None:
            await ctx.send(f"{ctx.author.mention} Please provide dice to roll. `!roll #d#`")

        try:
            num, sides = map(int, dice.lower().split("d"))
            if num <= 0 or sides <= 0:
                raise ValueError()
        except ValueError:
            await ctx.send(f"{ctx.author.mention} Invalid format. Use `#d#` - ex: `2d6`.")
            return

        if num > 100:
            await ctx.send(f"{ctx.author.mention} You can only roll up to `100` times.")
            return

        if sides > 100:
            await ctx.send(f"{ctx.author.mention} Maximum dice size is `100`.")
            return

        if sides not in [4, 6, 8, 10, 12, 20, 100]:
            await ctx.send(f"{ctx.author.mention} Invalid dice size. `(4, 6, 8, 10, 12, 20, 100)`")
            return

        rolls = [random.randint(1, sides) for _ in range(num)]
        total = sum(rolls)
        if num == 1:
            await ctx.send(f"{ctx.author.mention} rolled a **{rolls[0]}** (1d{sides})")
        else:
            rolls_str = ", ".join(map(str, rolls))
            await ctx.send(f"{ctx.author.mention} rolled ({num}d{sides}): → **{total}** [{rolls_str}]")