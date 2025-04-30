import os
import sys
import asyncio
import logging
import importlib.util
from rich.console import Console
from discord.ext import commands
from inc.db import drop_table
from clang import random_decimal_sleep, ainput

# Pretty console
console = Console(force_terminal=True, markup=True)

importlib.invalidate_caches()

class TerminalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_terminal_input(self):
        loop = asyncio.get_event_loop()
        while True:
            command = await loop.run_in_executor(None, input, "☠ -> ")
            parts  = command.strip().split(maxsplit=2)
            match parts:
                case ["help"]:
                    console.print("Available commands: help, reload, restart, say, clear, init, exit\n")

                case ["help", cmd]:
                    if   cmd == "help":    console.print("Prints the available commands\n")
                    elif cmd == "reload":  console.print("Reloads all plugins. This doesn't seem to work well\n")
                    elif cmd == "restart": console.print("Restarts Clang\n")
                    elif cmd == "say":     console.print("Usage: say <channel_id> <message>\n")
                    elif cmd == "clear":   console.print("Clears the screen\n")
                    elif cmd == "init":    console.print("Reinitializes the database (drops all tables) Cannot be undone\n")
                    elif cmd == "exit":    console.print("Attempts to shut down Clang gracefully\n")

                case ["exit"]:
                    console.print("Shutting down...")
                    await self.bot.close()
                    if self.bot.http._session:
                        await self.bot.http._session.close()
                    await self.bot.loop.shutdown_asyncgens()
                    sys.exit(0)

                case ["say", channel_id_str, message]:
                    try:
                        cid = int(channel_id_str)
                        chan = self.bot.get_channel(cid)
                        if not chan:
                            console.print(f"Error: Channel {cid} not found.\n")
                            continue
                        await chan.send(message)
                        console.print(f"Sent to #{chan.name}: {message}\n")
                    except ValueError:
                        console.print("Error: Invalid channel ID.\n")
                    except Exception as e:
                        console.print(f"Error: {e}\n")

                case ["clear"]:
                    os.system("cls" if os.name == "nt" else "clear")

                case ["restart"]:
                    os.system("cls" if os.name == "nt" else "clear")
                    os.execv(sys.executable, [sys.executable] + sys.argv)

                case ["init"]:
                    console.print(
                        "[bold yellow][?][/bold yellow] Are you sure you want to reinitialize the database? "
                        "This will drop all tables and cannot be undone. (y/N): ",
                        end="",
                    )
                    confirm = (await ainput("")).strip().lower() or "n"
                    if confirm == "y":
                        console.print("Okay, you asked for it. Reinitializing...", style="bold red")
                        await random_decimal_sleep(1, 1)
                        for tbl in ["config", "cookies", "channelperms", "guilds"]:
                            drop_table(tbl)
                            console.print(f"Dropped table '{tbl}'", style="bold cyan")
                            await random_decimal_sleep(1, 1)
                        console.print("Restarting Clang…", style="bold yellow")
                        await random_decimal_sleep(1, 1)
                        os.system("cls" if os.name == "nt" else "clear")
                        os.execv(sys.executable, [sys.executable] + sys.argv)

                case ["reload"]:
                    console.print("[bold yellow]Reloading all cogs…[/bold yellow]", style="yellow")
                    await random_decimal_sleep(0, 0.4)

                    # Iterate over every Python file in /plugins folder
                    for filename in os.listdir("./plugins"):
                        if filename.endswith(".py") and filename != "__init__.py":
                            ext_name = f"plugins.{filename[:-3]}"  # Remove .py extension
                            try:
                                if ext_name in self.bot.extensions:
                                    self.bot.unload_extension(ext_name)  # Unload before reloading
                                    console.print(f"[bold cyan][-][/bold cyan] Unloaded {ext_name}")
                                    await random_decimal_sleep(0, 0.4)
                                self.bot.load_extension(ext_name)  # Load the extension
                                console.print(f"[bold green][✔][/bold green] Reloaded {ext_name}")
                                await random_decimal_sleep(0, 0.4)
                            except Exception as e:
                                console.print(f"[bold red][X][/bold red] Failed to reload {ext_name}: {e}")
                                await random_decimal_sleep(0, 0.4)
                            await random_decimal_sleep(0, 0.4)

                    console.print("[bold cyan]==>[/bold cyan] Done.\n", style="bold")



    @commands.Cog.listener()
    async def on_ready(self):
        # Ensure the bot is actually ready
        console.print("[bold green]Bot is ready! Starting the terminal input...[/bold green]", style="bold green")
        # start shell loop once
        self.bot.loop.create_task(self.process_terminal_input())

def setup(bot):
    bot.add_cog(TerminalCommands(bot))
