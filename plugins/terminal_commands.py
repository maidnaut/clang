import discord
from discord.ext import commands
import sys
import asyncio
import logging

# Disable aiohttp warning logs
logging.getLogger("aiohttp.client").setLevel(logging.CRITICAL)

class TerminalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_terminal_input(self):
        loop = asyncio.get_event_loop()

        while True:
            command = await loop.run_in_executor(None, input, "☠ -> ")
            command = command.strip()

            parts = command.split(maxsplit=2)  # important: limit splits
            match parts:
                case ["help"]:
                    print("Available commands: 'help', 'stop', 'say'\n")

                case ["help", command]:
                    if command == "help":
                        print("Prints the available commands.\n")
                    
                    if command == "stop":
                        print("Attempts to gracefully shutdown Clang.\n")

                    if command == "say":
                        print("Sends a message in the supplied channel id. `say: <channel:id> <message>`\n")

                case ["stop"]:
                    print("Shutting down...")
                    await self.bot.close()
                    if self.bot.http._session:
                        await self.bot.http._session.close()
                    await self.bot.loop.shutdown_asyncgens()
                    sys.exit(0)

                case ["say", channel_id_str, message]:
                    try:
                        channel_id = int(channel_id_str)
                        channel = self.bot.get_channel(channel_id)

                        if not channel:
                            print(f"Error: Channel {channel_id} not found.\n")
                            continue

                        await channel.send(message.strip())
                        print(f"#{channel.name}: {message}\n")

                    except ValueError:
                        print("Error: Invalid channel ID.\n")
                    except Exception as e:
                        print(f"Error: {e}")

                case ["say"]:
                    print("Usage: say <channel:id> <message>\n")

                case _:
                    print("I don't know that word. Use 'help' for more information.\n")




    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.process_terminal_input())  # Start reading terminal input when the bot is ready

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(TerminalCommands(bot))
