import discord
import sqlite3
from discord.ext import commands
from db import db_create, db_read, db_update

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

# This will be added to the bot when the cog is loaded
def setup(bot):
    bot.add_cog(ThankListener(bot))
