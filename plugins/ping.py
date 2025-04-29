from discord.ext import commands
from db import db_create, db_read, db_update

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        # Check if the 'ping_usage' key exists
        count = db_read('ping_usage')

        if count is None:
            # If the key doesn't exist, initialize it to 0
            count = 0
            db_create('ping_usage', str(count))  # Create the 'ping_usage' entry in the database

        # Increment the usage count
        count = int(count) + 1  # Convert to int, increment, and then update back to the database
        db_update('ping_usage', str(count))  # Update the count in the database

        # Send the current usage count back to the user
        await ctx.send(f"Pong! This command has been used {count} times.")

    @commands.command()
    async def reset_ping(self, ctx):
        # Reset the 'ping_usage' counter to 0 in the database
        db_update('ping_usage', '0')
        await ctx.send("Ping usage count has been reset.")

# This setup function adds the cog to the bot
def setup(bot):
    bot.add_cog(PingCog(bot))
