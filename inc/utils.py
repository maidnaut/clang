import random, asyncio
from inc.db import *
from rich.console import Console

# Pretty print
console = Console(force_terminal=True, markup=True)
print = console.print

# Decimal sleep
async def random_decimal_sleep(min_sleep: float, max_sleep: float):
    await asyncio.sleep(random.uniform(min_sleep, max_sleep))

# Shell inputs
async def ainput(prompt: str = "") -> str:
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

# Numeric inputs
async def get_numeric_input(prompt, allow_empty=True, default="0"):
    while True:
        console.print(prompt, end="", highlight=False)

        val = (await ainput("")).strip()

        if allow_empty and val == "":
            return default

        if val.isdigit():
            return val

        console.print("[bold red][X][/bold red] Please enter a valid numeric ID.")
        await asyncio.sleep(0.1)

# Check for the bot token in the database, if it doesn't exist then ask for it
async def check_for_token():
    """Prompt for or fetch the bot token from the DB."""
    if not table_exists("bot_token"):
        new_db("bot_token", [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("bot_token", "TEXT")
        ])

    rows = db_read("bot_token", ["bot_token:*"])
    if not rows:
        console.print(
            "[bold yellow][?][/bold yellow] What is your bot token? (Clang won’t work without it): ",
            end=""
        )
        token = (await ainput("")).strip()
        db_insert("bot_token", ["bot_token"], [token])
        console.print("[bold green][✔][/bold green] Token registered.\n")
        await random_decimal_sleep(0.8, 1.2)
        return token

    return rows[0][1]

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

# Permission system
async def has_perms(ctx):

    elevation_config = db_read("config", [f"guild_id:{ctx.guild.id}", "name:elevation_enabled", "enabled:*"])
    elevation_enabled = elevation_config[0][1]

    roles = db_read("channelperms", [f"guild_id:{ctx.guild.id}", "*:*"])

    return True

    if any(row[1] != str(ctx.guild.id) for row in roles):

        submod = roles[0][3]
        mod = roles[0][3]
        op = roles[0][3]
        admin = roles[0][3]
        root = roles[0][3]
        owner = roles[0][3]

        if elevation_enabled == "y":
            if any(role.id in [op, root, owner] for role in ctx.author.roles):
                return True
            else:
                await ctx.send("!op?")
                return False
        elif any(role.id in [mod, admin, owner] for role in ctx.author.roles):
            return True
        else:
            return False