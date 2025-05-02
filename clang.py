import os, sys, time, random, asyncio, discord
from inc.db import *
from pathlib import Path
from discord.ext import commands
from rich.console import Console
from inc.terminal import ClangShell
from inc.utils import *

version = "0.4.3a"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    TOKEN = loop.run_until_complete(check_for_token())
finally:
    pass

# Pycord stuff
activity = discord.Game(name="!help")
bot = commands.Bot(command_prefix="!", activity=activity, help_command=None, intents=discord.Intents.all())
bot.add_cog(ClangShell(bot))

# global dict
bot.globals = {}
bot.globals["guilds"] = []
bot.globals["TOKEN"] = ""
bot.globals["init_db"] = False

#################################################################################
# Start Clang
#################################################################################
async def start_bot():

    # Check for token
    bot.globals["TOKEN"] = await check_for_token()

    min_wait = 0
    max_wait = 0.1

    print("__________________________________________________________________________\n")
    await random_decimal_sleep(0.1, 0.3)
    print("[bold red]Cosmic Arp © 2025[/bold red] - maidnaut@gnamil.com\n\n")
    await random_decimal_sleep(0.1, 0.3)

    # CLANG
    print('''     √√√√∞√√√≈÷      ''')
    await random_decimal_sleep(min_wait, max_wait)
    print('''  ×√√≈√√√√√√√  √     ''')
    await random_decimal_sleep(min_wait, max_wait)
    print('''+×+××≠√√    √√       ''')
    await random_decimal_sleep(min_wait, max_wait)
    print(''' ≈+××√√√    √√×≠∞    ''')
    await random_decimal_sleep(min_wait, max_wait)
    print('''×≈√ √√√√√√÷√√√≈≈√√   ''')
    await random_decimal_sleep(min_wait, max_wait)
    print(''' ×≈≈√≠∞√-√ ∞√√√       ''')
    await random_decimal_sleep(min_wait, max_wait)
    print('''  ≈√√√= √≈             ''')
    await random_decimal_sleep(min_wait, max_wait)
    print('''    √√√√≈÷√  ××√√√√      ''')
    await random_decimal_sleep(min_wait, max_wait)
    print('''           ××××××  × ''') 
    await random_decimal_sleep(min_wait, max_wait)
    print("\n")

    await random_decimal_sleep(0.2, 0.5)
    print("__________________________________________________________________________\n")
    await random_decimal_sleep(0.4, 0.8)
    print(f"\n[bold cyan]==>[/bold cyan] Clang [cyan]v{version}[/cyan] is starting...", highlight=False)
    await random_decimal_sleep(0.4, 0.8)

    # Connect to database
    await connect()

    # Now start the bot
    bot_token = db_read("bot_token", ["bot_token:*"])
    bot.globals["TOKEN"] = bot_token[0][1]
    await bot.start(bot.globals["TOKEN"])

@bot.event
async def on_ready():

    # Check guilds
    await check_guilds()

    # Check environment variables
    await check_env()

    # Check for shell
    shell = bot.get_cog("ClangShell")
    if shell:
        print("[bold cyan]==>[/bold cyan] Shell interface initialized")
        await random_decimal_sleep(0.1,0.4)
    else:
        print("[bold red][X][/bold red] Shell could not start")
        return

    # Load plugins
    print("[bold cyan]==>[/bold cyan] Loading plugins...", highlight=False)
    await random_decimal_sleep(0.1,0.4)
    print ("\n")
    await load_plugins()
    
    # Schedule a task for the shell or it won't work
    if shell:
        bot.loop.create_task(shell.process_terminal_input())

#################################################################################
# Connect to database
#################################################################################
async def connect():

    # Database setup

    await random_decimal_sleep(0.4,0.8)
    print(f"[bold cyan]==>[/bold cyan] Connecting to database")
    await random_decimal_sleep(0.1,0.4)

    if not os.path.exists(DB_FILE):
        print(f"[bold cyan]==>[/bold cyan] Database doesn't exist. Creating...", highlight=False)
        await random_decimal_sleep(0.1,0.4)
        try:
            open(DB_FILE, "x").close()
            print(f"[bold cyan]==>[/bold cyan] Database created successfully.")
            await random_decimal_sleep(0.8,1.2)

        except Exception as e:
            print(f"[bold red][X] ERROR:[/bold red] Could not create database: {e}")
            return
            
    print(f"[bold cyan]==>[/bold cyan] Database connection established")
    await random_decimal_sleep(0.4,0.8)

#################################################################################
# Check environment variables
#################################################################################
def load_plugins():
    plugins_path = Path("plugins")
    for file in plugins_path.glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = f"plugins.{file.stem}"
        try:
            importlib.import_module(module_name)
        except Exception as e:
            continue

async def check_env():

    # Check if environment variables exist

    if not table_exists("config"):
        new_db("config", [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("guild_id", "TEXT"),
            ("name", "TEXT"),
            ("enabled", "TEXT")
        ])

    config_check = db_read("config", ["*:*"])
    if not config_check:

        print(f"[bold cyan]==>[/bold cyan] Environment variables not found. Entering setup\n")
        await random_decimal_sleep(0.8,1.2)

        PLUGINS = {}
        def register_plugins(name: str, func: callable):
            PLUGINS[name] = func

        for guild in bot.guilds:
            gid = str(guild.id)
            name = guild.name

            console.print(f"[bold yellow][?][/bold yellow] Setup configuration for {name}? (Y/n): ", end="", highlight=False)
            response = (await ainput("")).strip().lower() or "y"

            if response == "y":
                await install(gid, name)
        
        print("\nSetup complete. Edit the configs at any time in the terminal.\n")
        await random_decimal_sleep(0.4,0.8)
    
    else:
        print(f"[bold cyan]==>[/bold cyan] Loaded environment variables")
        await random_decimal_sleep(0.1, 0.4)

#################################################################################
# Run the init
#################################################################################

async def install(guild_id, guild_name):

    # Setup questions

    print(f"\n[bold magenta]--- Setup for {guild_name} ---[/bold magenta]\n")

    console.print("[bold yellow][?][/bold yellow] Enable fun commands? Ex: !clang !fortune etc (Y/n): ", end="", highlight=False)
    use_fun = (await ainput("")).strip().lower() or "y"

    console.print("[bold yellow][?][/bold yellow] Enable utility commands? Ex: !whois !serverinfo etc (Y/n): ", end="", highlight=False)
    use_utils = (await ainput("")).strip().lower() or "y"

    console.print("[bold yellow][?][/bold yellow] Enable the moderation suite? (Y/n): ", end="", highlight=False)
    use_mod = (await ainput("")).strip().lower() or "y"

    console.print("[bold yellow][?][/bold yellow] Enable ticket functionality? (Y/n): ", end="", highlight=False)
    use_tickets = (await ainput("")).strip().lower() or "y"

    console.print("[bold yellow][?][/bold yellow] Enable logging functionality? (Y/n): ", end="", highlight=False)
    use_logging = (await ainput("")).strip().lower() or "y"

    console.print("[bold yellow][?][/bold yellow] Enable user notes? (Y/n): ", end="", highlight=False)
    use_notes = (await ainput("")).strip().lower() or "y"

    console.print("[bold yellow][?][/bold yellow] Enable cookies? (Y/n): ", end="", highlight=False)
    use_cookies = (await ainput("")).strip().lower() or "y"

    if use_mod == "y":

        console.print("[bold yellow][?][/bold yellow] Enable the use of a sub_mod with limited permissions? (Y/n): ", end="", highlight=False)
        submod_enabled = (await ainput("")).strip().lower() or "y"

        console.print("[bold yellow][?][/bold yellow] Enable elevated permission functionality? (Y/n): ", end="", highlight=False)
        elevation_enabled = (await ainput("")).strip().lower() or "y"

    else:
        submod_enabled = "n"
        elevation_enabled ="n"

    # Do a whole bunch of stuff to set up the db here

    try:
        print("[bold cyan]==>[/bold cyan] Creating databases...", highlight=False)
        await random_decimal_sleep(0,0.3)
        if use_cookies == "y":
            new_db("cookies", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("user_id", "TEXT"), ("cookies", "INTEGER")])
        new_db("channelperms", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("name", "TEXT"), ("channelperm", "TEXT")])
        new_db("commands", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("name", "TEXT"), ("enabled", "TEXT")])

        print("[bold cyan]==>[/bold cyan] Databases created. Populating...", highlight=False)
        await random_decimal_sleep(0,0.3)

        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "use_fun", use_fun])
        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "use_utils", use_utils])
        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "use_mod", use_mod])
        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "use_tickets", use_tickets])
        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "use_logging", use_logging])
        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "use_notes", use_notes])
        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "use_cookies", use_cookies])

        db_insert("commands", ["guild_id", "name", "enabled"], [guild_id, "clang", "1"])
        db_insert("commands", ["guild_id", "name", "enabled"], [guild_id, "fortune", "1"])
        db_insert("commands", ["guild_id", "name", "enabled"], [guild_id, "flip", "1"])
        db_insert("commands", ["guild_id", "name", "enabled"], [guild_id, "roll", "1"])

        print("[bold green][✔][/bold green] Use flags set.")
        await random_decimal_sleep(0,0.3)

        if use_cookies == "y":
            new_db("cookie_rate", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("rate", "INTEGER")])
            db_insert("cookie_rate", ["guild_id", "rate"], [guild_id, 100])
            print("[bold green][✔][/bold green] Default random chance of cookie drops set to 1 in 100 messages.")
            await random_decimal_sleep(0,0.3)

        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "ticket_category", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "join_channel", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "log_channel", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "modlog_channel", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "ticketlog_channel", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "adminticketlog_channel", ""])
        print("[bold green][✔][/bold green] Logging channels registered.")
        await random_decimal_sleep(0,0.3)

        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "submod_enabled", submod_enabled])
        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "elevation_enabled", elevation_enabled])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "submod_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "mod_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "elev_mod_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "admin_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "elev_admin_role", ""])
        print("[bold green][✔][/bold green] Roles registered.")
        await random_decimal_sleep(0,0.3)

        print("[bold cyan]==>[/bold cyan] Finalizing...\n", highlight=False) # I know this does nothing but the aesthetics are cool
        await random_decimal_sleep(0.8,1.4)

        bot.globals["init_db"] = True

    except Exception as e:
        print(f"[bold red][X][/bold red] Failed to initialize: {e}")
        return

#################################################################################
# Check for  guilds
#################################################################################
async def check_guilds():

    # Update guilds table if it doesn't exist

    if not table_exists("guilds"):
        new_db("guilds", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_name", "TEXT"), ("guild_id", "TEXT")])

    # Fetch guilds
    current_guild_ids = [str(guild.id) for guild in bot.guilds]
    existing_guilds = db_read("guilds", ["guild_id:*"])
    
    # Prep guilds list
    guilds_to_delete = []
    for guild_data in existing_guilds:
        db_guild_id = guild_data[2]  # Correct: "guild_id" is at index 2
        if db_guild_id not in current_guild_ids:
            guilds_to_delete.append(db_guild_id)

    # Delete guilds from the database that the bot is no longer part of
    if guilds_to_delete:
        for guild_id in guilds_to_delete:
            db_delete("guilds", ["guild_id"], [guild_id])
            print(f"[bold cyan]==>[/bold cyan] Deleted guild {guild_id} from the database. Clang is no longer there.")

    # Update the database with any new guilds
    for guild in bot.guilds:
        guild_data = [guild.name, str(guild.id)]
        
        existing_guild = db_read("guilds", [f"guild_id:{guild.id}"])

        if not existing_guild:
            db_insert("guilds", ["guild_name", "guild_id"], guild_data)
            print(f'[bold cyan]==>[/bold cyan] Added guild "{guild.name}" to the database. ({guild.id}).')

        bot.globals["guilds"].append([guild.name, str(guild.id)])
        
    for guild in bot.guilds:
        print(f"[bold cyan]==>[/bold cyan] Clang is present in {guild.name}")
        await random_decimal_sleep(0.1, 0.3)

#################################################################################
# Load plugins
#################################################################################
async def load_plugins():

    # Search all plugins in /plugins and gracefully fail on any errors

    await random_decimal_sleep(0, 0.4)

    for filename in os.listdir("./plugins"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                bot.load_extension(f"plugins.{filename[:-3]}")
                print(f"[bold green][✔][/bold green] Loaded plugin/{filename}")
                await random_decimal_sleep(0, 0.4)
            except Exception as e:
                print(f"[bold red][X][/bold red] Failed to load plugin {filename}: {e}")
                await random_decimal_sleep(0, 0.4)
                
    print("\n")
    await random_decimal_sleep(0.8, 1.2)

    if bot.globals["init_db"]:
        print("Clang is alive. (Hint: run `help`)\n")
    else:
        print(f"Clang is awake. (Hint: run 'help')\n")
    
    await random_decimal_sleep(0.8, 1.2)

if __name__ == "__main__":
    loop.run_until_complete(start_bot())