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

class ClangShell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_plugins(self):
        for file in os.listdir("./plugins"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    module_name = f"plugins.{file.stem}"
                except Exception as e:
                    continue

    def get_deps(self):
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

        return clean

    async def process_terminal_input(self):
        self.load_plugins()
        while True:
            command = await asyncio.get_event_loop().run_in_executor(
                 None, console.input, "[bold]☠ -> [/bold]"
            )
            parts = command.strip().split()
            match parts:
                case ["help"]:
                    all_cmds = "help, restart, setrole, setchannel, say, clear, deps, exit, "
                    all_cmds += ', '.join(sorted(PLUGIN.keys()))
                    all_cmds = ",".join(f"[cyan]{cmd}[/cyan]" for cmd in all_cmds.split(","))
                    print(f"Available commands: {all_cmds}\n", highlight=False)

                case ["help", cmd]:
                    if cmd == "help":
                        print("'help <command>': Prints the available commands\n", highlight=False)
                    elif cmd == "setrole":
                        print("'setrole [role] [id] [guild_id]': Sets the id for the specified role\n", highlight=False)
                    elif cmd == "setchannel":
                        print("'setchannel <channel> <id>': Sets the id for the specified channel or category\n", highlight=False)
                    elif cmd == "say":
                        print("'say <channel_id> <message>': Sends a message to the specified channel\n", highlight=False)
                    elif cmd == "clear":
                        print("'clear': Clears the screen\n", highlight=False)
                    elif cmd == "restart":
                        print("'restart': Restarts Clang\n", highlight=False)
                    elif cmd == "deps":
                        print("'deps': Lists all of Clang's dependencies.\n", highlight=False)
                    elif cmd == "exit":
                        print("'exit': Attempts to shut down Clang gracefully\n", highlight=False)
                    else:
                        info = PLUGIN.get(cmd)
                        if info:
                            console.print(f"{escape(info['help'])}\n", highlight=False)
                        else:
                            console.print(f"No help entry for '{cmd}'\n", highlight=False)

                case ["restart"]:
                    os.system("cls" if os.name == "nt" else "clear")
                    os.execv(sys.executable, [sys.executable] + sys.argv)

                case ["say", channel_id_str, *message_parts]:
                    try:
                        cid = int(channel_id_str)
                        chan = await self.bot.fetch_channel(cid)
                        message = " ".join(message_parts)
                        
                        if not message:
                            print("Error: Message cannot be empty\n")
                            continue
                            
                        await chan.send(message)
                        print(f"Sent to #{chan.name}: {message}\n")
                    except ValueError:
                        print("Error: Invalid channel ID format\n")
                    except discord.Forbidden:
                        print(f"Error: Missing permissions in channel {cid}\n")
                    except discord.NotFound:
                        print(f"Error: Channel {cid} not found\n")
                    except discord.HTTPException as e:
                        print(f"Error: Discord API failure - {e}\n")
                    except Exception as e:
                        print(f"Unexpected error: {type(e).__name__} - {e}\n")

                case ["clear"]:
                    os.system("cls" if os.name == "nt" else "clear")

                case ["deps"]:
                    deps = self.get_deps()
                    print("[", highlight=False)
                    for dep in deps:
                        print(f"    '{dep}',", highlight=False)
                    print("]", highlight=False)

                case ["exit"]:
                    console.print("Shutting down...")
                    await self.bot.close()
                    if self.bot.http._session:
                        await self.bot.http._session.close()
                    await self.bot.loop.shutdown_asyncgens()
                    sys.exit(0)

                case ["setrole", *args]:
                    usage = "setrole [role] [id] [guild_id]"
                    roles = ["s", "m", "o", "a", "r", "submod", "mod", "op", "admin", "root"]

                    while True:
                        if not args:
                            print(f"Sets the id for each role - Roles: (s)ubmod, (m)od, (o)p, (a)dmin, (r)oot \nUsage: {usage}\n", markup=False, highlight=False)
                            break
                            
                        first = args[0]
                        if first not in roles:
                            print(f"[bold red][X][/bold red] Error: Unknown role '{first}'\nUsage: {usage}\n", markup=False, highlight=False)
                            break

                        if len(args) < 2:
                            print(f"[bold red][X][/bold red] Error: Missing role ID\nUsage: {usage}\n", markup=False, highlight=False)
                            break

                        role_id = args[1]
                        guild_id = args[2] if len(args) > 2 else None

                        role = args[0]
                        if role == "s": role = "submod"
                        if role == "m": role = "mod"
                        if role == "o": role = "op"
                        if role == "a": role = "admin"
                        if role == "r": role = "root"

                        if not role_id.isdigit():
                            print(f"[bold red][X][/bold red] Error: Invalid role ID '{role_id}'\nUsage: {usage}\n", markup=False, highlight=False)
                            break

                        if guild_id and not guild_id.isdigit():
                            print(f"[bold red][X][/bold red] Error: Invalid guild ID '{guild_id}'\nUsage: {usage}\n", markup=False, highlight=False)
                            break

                        shorthand_map = {
                            "s": "submod", "m": "mod", "o": "op",
                            "a": "admin", "r": "root"
                        }
                        role_name = shorthand_map.get(first, first)

                        if not guild_id:
                            print("[bold red][X][/bold red] Error: No guild ID provided\nUsage: {usage}\n", markup=False, highlight=False)
                            break

                        db_update("roles", [f"guild_id:{guild_id}", f"name:{role}_role"], [("role", role_id)])
                        print(f"[bold green][✔][/bold green]  Updated role '{role_name}_role' with ID {role_id} for guild {guild_id}")
                        break

                case [cmd, *args]:
                    command = PLUGIN.get(cmd)
                    if command:
                        command["func"](args)
                    else:
                        print(f"Clang: Command not found: '{cmd}'")


def setup(bot):
    bot.add_cog(ClangShell(bot))
