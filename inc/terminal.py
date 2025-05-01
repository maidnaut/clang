import os
import sys
import importlib
import asyncio
import traceback
import subprocess
import json
from rich.console import Console
from rich.markup import escape
from discord.ext import commands
from pathlib import Path
from inc.db import *
from inc.utils import *
from importlib.metadata import distributions

# Pretty console
console = Console(force_terminal=True, markup=True)
importlib.invalidate_caches()

# Register Plugins
PLUGIN: dict[str, dict[str, any]] = {}
def register_plugin(name: str, help: str, func: callable):
    """
    Register a shell command with its help text and handler.
    """
    PLUGIN[name] = {
        "help": help.strip(),
        "func": func
    }

class ClangShell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_plugins(self):
        plugins_path = Path("plugins")
        for file in plugins_path.glob("*.py"):
            if file.name.startswith("_"):
                continue
            module_name = f"plugins.{file.stem}"
            try:
                importlib.import_module(module_name)
            except Exception:
                continue

    def get_clean_dependencies(self):
        try:
            raw = subprocess.check_output(
                [sys.executable, "-m", "pipdeptree", "--json-tree"],
                stderr=subprocess.DEVNULL
            )
            tree = json.loads(raw)
        except Exception:
            tree = []

        exclude: set[str] = set()
        def collect(pkg):
            key = pkg["package"]["key"]
            if key in exclude:
                return
            exclude.add(key)
            for dep in pkg.get("dependencies", []):
                collect(dep)

        for pkg in tree:
            if pkg["package"]["key"] in ("py-cord", "pycord", "discord.py", "discord"):
                collect(pkg)

        all_keys = {d.metadata["Name"].lower() for d in distributions()}
        clean = sorted(all_keys - exclude)

        return ["python", "pycord"] + clean

    async def process_terminal_input(self):
        self.load_plugins()
        while True:
            command = await asyncio.get_event_loop().run_in_executor(
                 None, console.input, "[bold]☠ -> [/bold]"
            )
            parts = command.strip().split()
            match parts:
                case ["help"]:
                    all_cmds = "help, restart, say, clear, reset, deps, exit, "
                    all_cmds += ', '.join(sorted(PLUGIN.keys()))
                    all_cmds = ",".join(f"[cyan]{cmd}[/cyan]" for cmd in all_cmds.split(","))
                    console.print(f"Available commands: {all_cmds}\n", highlight=False)

                case ["help", cmd]:
                    if cmd == "help":
                        console.print("'help <command>': Prints the available commands\n", highlight=False)
                    elif cmd == "restart":
                        console.print("'restart': Restarts Clang\n", highlight=False)
                    elif cmd == "say":
                        console.print("'say <channel_id> <message>': Sends a message to the specified channel\n", highlight=False)
                    elif cmd == "clear":
                        console.print("'clear': Clears the screen\n", highlight=False)
                    elif cmd == "reset":
                        console.print("'reset': Reinitializes the database (drops all tables) Cannot be undone\n", highlight=False)
                    elif cmd == "deps":
                        console.print("'deps': Lists all of Clang's dependencies.\n", highlight=False)
                    elif cmd == "exit":
                        console.print("'exit': Attempts to shut down Clang gracefully\n", highlight=False)
                    else:
                        info = PLUGIN.get(cmd)
                        if info:
                            console.print(f"{escape(info['help'])}\n", highlight=False)
                        else:
                            console.print(f"No help entry for '{cmd}'\n", highlight=False)

                case ["restart"]:
                    os.system("cls" if os.name == "nt" else "clear")
                    os.execv(sys.executable, [sys.executable] + sys.argv)

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

                case ["reset"]:
                    console.print(
                        "[bold yellow][?][/bold yellow] Are you sure you want to reinitialize the database? "
                        "This will drop ALL tables and cannot be undone. (y/N): ",
                        end="",
                    )
                    confirm = (await asyncio.get_event_loop().run_in_executor(None, console.input)).strip().lower() or "n"
                    if confirm == "y":
                        console.print("Okay, you asked for it. Reinitializing...", style="bold red")
                        await asyncio.sleep(1)
                        for tbl in ["config", "cookies", "channelperms", "guilds"]:
                            drop_table(tbl)
                            console.print(f"Dropped table '{tbl}'", style="bold cyan")
                            await asyncio.sleep(1)
                        console.print("Restarting Clang…", style="bold yellow")
                        await asyncio.sleep(1)
                        os.system("cls" if os.name == "nt" else "clear")
                        os.execv(sys.executable, [sys.executable] + sys.argv)

                case ["deps"]:
                    deps = self.get_clean_dependencies()
                    console.print("[", highlight=False)
                    for dep in deps:
                        console.print(f"    '{dep}',", highlight=False)
                    console.print("]", highlight=False)

                case ["exit"]:
                    console.print("Shutting down...")
                    await self.bot.close()
                    if self.bot.http._session:
                        await self.bot.http._session.close()
                    await self.bot.loop.shutdown_asyncgens()
                    sys.exit(0)

                case [cmd, *args]:
                    command = PLUGIN.get(cmd)
                    if command:
                        command["func"](args)
                    else:
                        console.print(f"Clang: Command not found: '{cmd}'")


def setup(bot):
    bot.add_cog(ClangShell(bot))
