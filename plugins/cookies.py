import discord, os, asyncio, argparse
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

    # Ensure the rate exists in the database (create if missing)
    def ensure_rate_exists(self, guild_id):

        if not table_exists("cookie_rate"):
            new_db("cookie_rate", f"guild_id:{guild_id}", 10)

            rate = db_read("cookie_rate", [f"guild_id:{guild_id}"])
            if rate is None:
                return 10
            return int(rate)

    # Ensure cookies exist and the table is initialized if needed
    def ensure_cookies_exists(self, guild_id, user_id):

        if not table_exists("cookies"):
            
            cookies = db_read("cookies", [f"guild_id:{guild_id}", (f"user_id:{user_id}")])

            if cookies is None:
                db_insert("cookies", ["user_id", "guild_id", "cookies"], [user_id, guild_id, "0"])


    # Command to show cookies and usage
    @commands.command()
    async def cookies(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id

        self.ensure_cookies_exists(guild_id, user_id)

        cookies = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])

        cookies_exist = cookies[1:]

        if len(cookies_exist) < 1:
            # Initialize with default cookies value
            db_insert("cookies", ["user_id", "guild_id", "cookies"], [user_id, guild_id, "0"])
            cookies = 0
        else:
            cookies = cookies[0][0]

        await ctx.send(f"You have {cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")

    # Command to eat a cookie (subtract one)
    @commands.command()
    async def nom(self, ctx):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)

        self.ensure_cookies_exists(guild_id, user_id)

        cookies = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
        if cookies is None or int(cookies) <= 0:
            await ctx.send("You don't have any cookies to eat!")
            return


        db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [int(cookies) - 1])
        db_update(user_id, guild_id, int(cookies) - 1)
        await ctx.send(f"You ate a cookie. You now have {int(cookies) - 1} cookies.")

    # Command to give a cookie to another user
    @commands.command()
    async def give(self, ctx, user: discord.User = None):
        if user is None:
            # No recipient supplied, return early and send a message
            await ctx.send("Giving cookies requires a mention: ``!give @user``")
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)
        guild_id = ctx.guild.id

        self.ensure_cookies_exists(guild_id, receiver_id)

        if sender_id == receiver_id:
            await ctx.send("You can't send cookies to yourself!")
            return
        
        sender_cookies = db_read("cookies", [f"user_id:{sender_id}", f"guild_id:{guild_id}"])
        if sender_cookies is None or int(sender_cookies) <= 0:
            await ctx.send(f"You don't have any cookies {ctx.author.name}!")
            return

        receiver_cookies = db_read("cookies", [f"user_id:{receiver_id}", f"guild_id:{guild_id}"])
        if receiver_cookies is None:
            self.ensure_cookies_exists(guild_id, receiver_id)
            receiver_cookies = 0

        db_update("cookies", [f"user_id:{sender_id}", f"guild_id:{guild_id}"], int(sender_cookies) - 1)
        db_update("cookies", [f"user_id:{receiver_id}", f"guild_id:{guild_id}"], int(receiver_cookies) + 1)

        await ctx.send(f"{user.name} received a cookie!")

    # Command to transfer cookies to another user (with amount)
    @commands.command()
    async def transfer(self, ctx, user: discord.User = None, amount: int = None):
        if user is None:
            await ctx.send("``!transfer <@user> <int>``")
            return
        
        if amount is None:
            await ctx.send("``!transfer <@user> <int>``")
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)
        guild_id = ctx.guild.id

        self.ensure_cookies_exists(guild_id, sender_id)

        sender_cookies = db_read("cookies", [f"user_id:{sender_id}", f"guild_id:{guild_id}"])
        if sender_cookies is None or int(sender_cookies) < amount:
            await ctx.send(f"You don't have enough cookies to transfer, {ctx.author.name}!")
            return

        receiver_cookies = db_read("cookies", [f"user_id:{receiver_id}", f"guild_id:{guild_id}"])
        if receiver_cookies is None:
            db_create(receiver_id, 0)  # Create receiver's entry if it doesn't exist
            receiver_cookies = 0

        db_update("cookies", [f"user_id:{sender_id}", f"guild.id:{guild_id}", [int(sender_cookies - amount)]])
        db_update("cookies", [f"user_id:{receiver_id}", f"guild.id:{guild_id}", [int(receiver_id + amount)]])

        await ctx.send(f"You transferred {amount} cookies to {user.name}. {ctx.author.name} now has {int(sender_cookies) - amount} cookies, and {user.name} now has {int(receiver_cookies) + amount} cookies.")

    # Command to set the rate of getting a cookie
    @commands.command()

    async def setrate(self, ctx, rate: int = None):
        if rate is None:
            if not await has_elevated_permissions(ctx):
                return

            await ctx.send("``!setrate <int>``")
            return

        if not await has_elevated_permissions(ctx):
            return

        # Update rate in database
        guild_id = ctx.guild.id
        db_update("cookie_rate", [(f"guild_id:{guild_id}", f"rate:{rate}")])
        await ctx.send(f"The cookie rate has been set to 1 in {rate} messages.")

    # Command to spawn cookies out of thin air and give them to a user
    @commands.command()
    async def airdrop(self, ctx, user: discord.User = None, amount: int = None):
        if user is None:
            if not await has_elevated_permissions(ctx):
                return

            await ctx.send("``!airdrop <@user> <int>``")
            return

        if amount is None:
            if not await has_elevated_permissions(ctx):
                return

            await ctx.send("``!airdrop <@user> <int>``")
            return

        if not await has_elevated_permissions(ctx):
            return
        
        # Add the cookies to the user
        guild_id = ctx.guild.id
        user_id = str(user.id)

        user_cookies = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
        if user_cookies is None:

            db_update("cookies", [f"guild_id:{guild_id}", [rate]])
            self.ensure_cookies_exists(user_id, guild_id)
            user_cookies = 0

        db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], user_cookies + amount)
        await ctx.send(f"{ctx.author.name} has airdropped {amount} cookies to {user.name}! {user.name} now has {int(user_cookies) + amount} cookies.")

    # Random chance to receive a cookie when sending a message
    @commands.Cog.listener()
    async def on_message(self, ctx, message = None):
        user_id = str(ctx.author.id)
        # Ignore messages from the bot
        if str(ctx.author.bot):
            return

        # Ensure rate exists in the database
        guild_id = ctx.guild.id
        rate = await ensure_rate_exists(guild_id, user_id)

        # 1 in X chance based on the rate value
        if random.randint(1, rate) == 1:
            user_cookies = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
            if user_cookies is None:
                self.ensure_cookies_exists(guild_id, user_id)
                user_cookies = 0
            db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [user_cookies + 1]);




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