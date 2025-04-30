from discord.ext import commands
from db import *

def new_db_act(guild_id, user_id):
    # Make sure the table exists before accessing it
    init_db("cookies", [("guild_id", "TEXT"), ("user_id", "TEXT"), ("cookies", "INTEGER")])
    
    # Now, try to read the record
    cookie_table = db_read("cookies", [f"guild_id:{guild_id}"])
    if cookie_table is not None:
        await ctx.send("Table created for this guild.")
    
    # If the table doesn't contain the cookie entry, initialize it with defaults
    if cookie_table is None:
        db_create("cookies", 
            ["user_id", "guild_id", "cookies"], 
            [user_id, guild_id, 0])  # Initialize with default values

class TestCog(commands.Cog):

    @commands.command()
    async def new_db(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id

        new_db(guild_id, user_id)

        cookies = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])

        if cookies[0] is None or cookies[1] is None:
            # Initialize with default cookies value
            db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [0])
            cookies = 0
        else:
            cookies = cookies[0][0]

        await ctx.send(f"You have {cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")


def setup(bot):
    bot.add_cog(TestCog(bot))
