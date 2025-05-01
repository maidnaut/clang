import os
import random
import discord
import sqlite3
from discord.ext import commands
from db import init_db, db_create, db_read, db_update
from dotenv import load_dotenv
from inc.permissions import has_elevated_permissions

register_command(
    name="cookies",
    help="cookies help",
    man="""
this is an example of the cookies man page
    """
)

# Load env vars
load_dotenv()
def get_int_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Missing {var_name} in .env file")
    return int(value)

# Load role IDs dynamically from .env file
MODERATOR_ROLE = get_int_env_var("moderatorRole")
ADMIN_ROLE = get_int_env_var("adminRole")
OPERATOR_ROLE = get_int_env_var("operatorRole")
ROOT_ROLE = get_int_env_var("rootRole")

# Database field for storing the cookie rate
DB_FILE = 'bot_data.db'

# Ensure the rate exists in the database (create if missing)
def ensure_rate_exists(guild_id):

    init_db("cookie_rate", f"guild_id:{guild_id}", 10)

    rate = db_read("cookie_rate", [f"guild_id:{guild_id}"])
    if rate is None:
        return 10
    return int(rate)

# Ensure cookies exist and the table is initialized if needed
def ensure_cookies_exists(guild_id, user_id):
    # Make sure the table exists before accessing it
    init_db("cookies", [("guild_id", "TEXT"), ("user_id", "TEXT"), ("cookies", "INTEGER")])
    
    # Now, try to read the record
    cookie_table = db_read("cookies", [f"guild_id:{guild_id}"])
    
    # If the table doesn't contain the cookie entry, initialize it with defaults
    if cookie_table is None:
        db_create("cookies", 
            ["user_id", "guild_id", "cookies"], 
            [user_id, guild_id, 0])  # Initialize with default values

# Create the CookieCog class
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

    # Command to show cookies and usage
    @commands.command()
    async def cookies(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id

        ensure_cookies_exists(guild_id, user_id)

        cookies = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])

        if cookies[0] is None or cookies[1] is None:
            # Initialize with default cookies value
            db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [0])
            cookies = 0
        else:
            cookies = cookies[0][0]

        await ctx.send(f"You have {cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")

    # Command to eat a cookie (subtract one)
    @commands.command()
    async def nom(self, ctx):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)
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

        if sender_id == receiver_id:
            await ctx.send("You can't send cookies to yourself!")
            return
        
        sender_cookies = db_read("cookies", [f"user_id:{sender_id}", f"guild_id:{guild_id}"])
        if sender_cookies is None or int(sender_cookies) <= 0:
            await ctx.send(f"You don't have any cookies {ctx.author.name}!")
            return

        receiver_cookies = db_read("cookies", [f"user_id:{receiver_id}", f"guild_id:{guild_id}"])
        if receiver_cookies is None:
            ensure_cookies_exists(guild_id, receiver_id)
            receiver_cookies = 0

        db_update("cookies", [f"user_id:{sender}", f"guild_id:{guild_id}"], int(sender_cookies) - 1)
        db_update("cookies", [f"user_id:{receiver_id}", f"guild_id:{guild_id}"], int(receiver_cookes) + 1)

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
        db_update("cookies", [f"guild_id:{guild_id}", [rate]])
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
            ensure_cookies_exists(user_id, guild_ud)
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
        rate = ensure_rate_exists(guild_id, user_id)

        # 1 in X chance based on the rate value
        if random.randint(1, rate) == 1:
            user_cookies = db_read(user_id)
            if user_cookies is None:
                ensure_cookies_exists(user_id, guild_id)
                user_cookies = 0
            db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [user_cookies + 1]);

# Initialize Cookie
def setup(bot):
    bot.add_cog(CookieCog(bot))

#######################################################

class ThankListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listen for replies containing the word 'thank' and give a free cookie to the recipient.
        """
        # Ensure the bot does not respond to its own messages
        if message.author == self.bot.user:
            return

        # Check if the message is a reply (it has a reference)
        if message.reference:
            try:
                # Fetch the original message being replied to
                original_message = await message.channel.fetch_message(message.reference.message_id)

                # Check if "thank" is in the reply (case-insensitive)
                if "thank" in message.content.lower():
                    # Give a free cookie to the user who was replied to (original_message.author)
                    await self.give_cookie(original_message.author, message.channel)
            except discord.NotFound:
                # In case the original message is deleted
                return

    async def give_cookie(self, user, channel):
        receiver_id = str(user.id)

        # Check if the receiver exists in the database, otherwise create it
        receiver_cookies = db_read(receiver_id)
        if receiver_cookies is None:
            db_create(receiver_id, 0)  # Create receiver's entry if it doesn't exist
            receiver_cookies = 0

        # Update the database
        db_update(receiver_id, int(receiver_cookies) + 1)

        # Send a message to the channel notifying the recipient
        await channel.send(f"{user.name} recieved a thank you cookie!")

# Initialize thanks cog
def setup(bot):
    bot.add_cog(ThankListener(bot))
