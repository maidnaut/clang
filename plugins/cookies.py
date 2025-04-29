import os
import random
import discord
from discord.ext import commands
from db import db_create, db_read, db_update
from dotenv import load_dotenv
from permissions import has_elevated_permissions

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
RATE_DB_KEY = "cookie_rate"

# Ensure the rate exists in the database (create if missing)
def ensure_rate_exists():
    rate = db_read(RATE_DB_KEY)
    if rate is None:
        # Create the rate in the database with a default value (e.g., 10)
        db_create(RATE_DB_KEY, 10)
        return 10  # Return the default rate when creating it
    return int(rate)  # Make sure to return an integer

# Create the CookieCog class
class CookieCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to show cookies and usage
    @commands.command()
    async def cookies(self, ctx):
        user_id = str(ctx.author.id)
        cookies = db_read(user_id)
        if cookies is None:
            db_create(user_id, 0)  # Initialize the user entry with 0 cookies
            cookies = 0

        await ctx.send(f"You have {cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")

    # Command to eat a cookie (subtract one)
    @commands.command()
    async def nom(self, ctx):
        user_id = str(ctx.author.id)
        cookies = db_read(user_id)
        if cookies is None or int(cookies) <= 0:
            await ctx.send("You don't have any cookies to eat!")
            return

        db_update(user_id, int(cookies) - 1)
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

        if sender_id == receiver_id:
            await ctx.send("You can't send cookies to yourself!")
            return
        
        sender_cookies = db_read(sender_id)
        if sender_cookies is None or int(sender_cookies) <= 0:
            await ctx.send(f"You don't have any cookies {ctx.author.name}!")
            return

        receiver_cookies = db_read(receiver_id)
        if receiver_cookies is None:
            db_create(receiver_id, 0)  # Create receiver's entry if it doesn't exist
            receiver_cookies = 0

        db_update(sender_id, int(sender_cookies) - 1)
        db_update(receiver_id, int(receiver_cookies) + 1)

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

        sender_cookies = db_read(sender_id)
        if sender_cookies is None or int(sender_cookies) < amount:
            await ctx.send(f"You don't have enough cookies to transfer, {ctx.author.name}!")
            return

        receiver_cookies = db_read(receiver_id)
        if receiver_cookies is None:
            db_create(receiver_id, 0)  # Create receiver's entry if it doesn't exist
            receiver_cookies = 0

        db_update(sender_id, int(sender_cookies) - amount)
        db_update(receiver_id, int(receiver_cookies) + amount)

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
        db_update(RATE_DB_KEY, rate)
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
        user_id = str(user.id)
        user_cookies = db_read(user_id)
        if user_cookies is None:
            db_create(user_id, 0)  # Create entry if not exists
            user_cookies = 0

        db_update(user_id, int(user_cookies) + amount)
        await ctx.send(f"{ctx.author.name} has airdropped {amount} cookies to {user.name}! {user.name} now has {int(user_cookies) + amount} cookies.")

    # Random chance to receive a cookie when sending a message
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot
        if message.author.bot:
            return

        # Ensure rate exists in the database
        rate = ensure_rate_exists()

        # 1 in X chance based on the rate value
        if random.randint(1, rate) == 1:
            user_id = str(message.author.id)
            user_cookies = db_read(user_id)
            if user_cookies is None:
                db_create(user_id, 0)  # Create entry if not exists
                user_cookies = 0

            db_update(user_id, int(user_cookies) + 1)

# Initialize cog
def setup(bot):
    bot.add_cog(CookieCog(bot))
