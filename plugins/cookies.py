import discord, os, random, asyncio, argparse
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):
    
    init_term()

    # Cogs
    bot.add_cog(CookieCog(bot))




#################################################################################




#################################################################################
# !cookies command suite
#################################################################################
class CookieCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Help info
        self.__help__ = {
            "cookies": {
                "args": "",
                "desc": "Shows your cookies and supplies commands",
                "perm": "everyone"
            },
            "nom": {
                "args": "",
                "desc": "Eats a cookie",
                "perm": "everyone"
            },
            "give": {
                "args": "<user>",
                "desc": "Gives the mentioned user one of your cookies",
                "perm": "everyone"
            },
            "transfer": {
                "args": "<user> (amount)",
                "desc": "Cookie credit transfer",
                "perm": "everyone"
            },
            "airdrop": {
                "args": "<user> (amount)",
                "desc": "Hack in cookies",
                "perm": "admin"
            },
            "setrate": {
                "args": "(amount)",
                "desc": "Sets the rate for the random chance to recieve cookies on every message",
                "perm": "admin"
            },
        }

    # Make sure the cookies for the user exists and return an amouunt
    def check_cookies(self, guild_id, user_id):
        # Read from database
        result = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
        
        if not result:  # No record exists
            try:
                db_insert("cookies", 
                        ["user_id", "guild_id", "cookies"],
                        [user_id, guild_id, 0])
                return 0
            except sqlite3.IntegrityError:
                # Handle rare case where record was created between read and insert
                result = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
                return result[0][3] if result else 0
        
        # Assuming columns are: id, guild_id, user_id, cookies
        return result[0][3]  # Return cookies value from 4th column

    # !coomies
    @commands.command()
    async def cookies(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id

        cookies = self.check_cookies(guild_id, user_id)

        await ctx.send(f"<@{ctx.author.id}> You have {cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")

    # !nom
    @commands.command()
    async def nom(self, ctx):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)

        cookies = self.check_cookies(guild_id, user_id)

        if cookies is None or cookies <= 0:
            await ctx.send("You don't have any cookies to eat!")
            return

        db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [("cookies", cookies - 1)])
        await ctx.send(f"<@{ctx.author.id}> You ate a cookie. You now have {cookies - 1} cookies.")

    # !give <user>
    @commands.command()
    async def give(self, ctx, user: discord.User = None):
        if user is None:
            return await ctx.send("Please mention a user: `!give @user`")

        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)
        guild_id = str(ctx.guild.id)  # Ensure this is string to match DB

        if sender_id == receiver_id:
            return await ctx.send("You can't send a cookie to yourself!")

        # Get current counts
        sender_cookies = self.check_cookies(guild_id, sender_id)
        receiver_cookies = self.check_cookies(guild_id, receiver_id)

        if sender_cookies < 1:
            return await ctx.send("You don't have any cookies to give!")

        # Update database - PROPER FORMAT:
        # Update sender
        db_update("cookies",
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"],
                [("cookies", sender_cookies - 1)])
        
        # Update receiver
        db_update("cookies",
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"],
                [("cookies", receiver_cookies + 1)])
        
        await ctx.send(f"<@{ctx.author.id}> gave a cookie to {user.mention}!")

    # !transfer <user> <int>
    @commands.command()
    async def transfer(self, ctx, user: discord.User = None, amount: int = None):
        if user is None or amount is None:
            await ctx.send("``!transfer <@user> <int>``")
            return
        
        if amount <= 0:
            await ctx.send("Amount must be positive!")
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)
        guild_id = ctx.guild.id

        sender_cookies = self.check_cookies(guild_id, sender_id)
        if sender_cookies < amount:
            await ctx.send(f"<@{ctx.author.id}> You don't have enough cookies to transfer that much!")
            return

        receiver_cookies = self.check_cookies(guild_id, receiver_id)

        # Update sender
        db_update("cookies", 
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"], 
                [("cookies", sender_cookies - amount)])
        
        # Update receiver
        db_update("cookies", 
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"], 
                [("cookies", receiver_cookies + amount)])

        await ctx.send(f"<@{ctx.author.id}> transferred {amount} cookies to {user.mention}!")

    # !setrate <int>
    @commands.command()
    async def setrate(self, ctx, rate: int = None):
        if not await has_perms(ctx):
            return
        
        if rate is None:
            await ctx.send("``!setrate <int>``")
            return
        
        if rate <= 0:
            await ctx.send("Rate must be positive!")
            return

        guild_id = ctx.guild.id
        # Update cookie_rate table instead of cookies table
        db_update("cookie_rate", 
                [f"guild_id:{guild_id}"], 
                [("rate", rate)])

        await ctx.send(f"Cookie drop rate set to 1 in {rate} messages.")

    # !airdrop <user> <int>
    @commands.command()
    async def airdrop(self, ctx, user: discord.User = None, amount: int = None):
        if not await has_perms(ctx):
            return
        
        if user is None or amount is None:
            await ctx.send("``!airdrop <@user> <int>``")
            return
        
        if amount <= 0:
            await ctx.send("Amount must be positive!")
            return

        guild_id = ctx.guild.id
        user_id = str(user.id)

        cookies = self.check_cookies(guild_id, user_id)
        db_update("cookies", 
                [f"user_id:{user_id}", f"guild_id:{guild_id}"], 
                [("cookies", cookies + amount)])

        await ctx.send(f"Airdropped {amount} cookies to {user.name}! They now have {cookies + amount} cookies.")

    # Random cookie drop
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        
        rate = db_read("cookie_rate", [f"guild_id:{guild_id}"])
        rate = int(rate[0][2]) if rate else 100
        
        if random.randint(1, rate) == 1:
            current = self.check_cookies(guild_id, user_id)
            db_update("cookies",
                    [f"user_id:{user_id}", f"guild_id:{guild_id}"],
                    [("cookies", current + 1)])

        thank_words = ["thank", "thx", "ty", "thanks", "tysm", "tyvm", "thnx"]
        contains_thank = any(word in message.content.lower() for word in thank_words)
        
        if contains_thank:
            thanked_users = []
            
            thanked_users.extend([u for u in message.mentions if u.id != message.author.id])
            
            if message.reference:
                try:
                    replied_msg = await message.channel.fetch_message(message.reference.message_id)
                    if replied_msg.author.id != message.author.id:
                        thanked_users.append(replied_msg.author)
                except:
                    pass
            
            thanked_users = list({u.id: u for u in thanked_users}.values())
            
            if thanked_users:
                for user in thanked_users:
                    uid = str(user.id)
                    current = self.check_cookies(guild_id, uid)
                    db_update("cookies",
                            [f"user_id:{uid}", f"guild_id:{guild_id}"],
                            [("cookies", current + 1)])
                
                # Send response
                if len(thanked_users) == 1:
                    await message.channel.send(f"{thanked_users[0].mention} received a thank you cookie!")
                else:
                    names = ", ".join(u.mention for u in thanked_users[:-1]) + f" and {thanked_users[-1].mention}"
                    await message.channel.send(f"{names} received thank you cookies!")




#################################################################################




#################################################################################
# Register terminal stuff
#################################################################################
def init_term():

    # Init some text we'll use later
    usage = "command_name [-args] [guild_id:optional]"
    
    example = """
    Usage example goes here
    """

    def function(args: list[str]):

        # Put the terminal response function here
        print("todo")

    # Help page & register
    register_plugin(
        name="template",
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