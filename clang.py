import os
import sys
import time
import json
import random
import asyncio
import sqlite3
import discord
from inc.db import *
from pathlib import Path
from discord.ext import commands
from rich.console import Console

version = "0.3"

# Pycord stuff
activity = discord.Game(name="!help")
bot = commands.Bot(command_prefix="!", activity=activity, help_command=None, intents=discord.Intents.all())

# Pretty print
console = Console(force_terminal=True, markup=True)
print = console.print

# Custim sleep function
async def random_decimal_sleep(min_sleep, max_sleep):
    sleep_time = random.uniform(min_sleep, max_sleep)
    await asyncio.sleep(sleep_time)

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
    print(f"\n[bold cyan]==>[/bold cyan] Clang [cyan]v{version}[/cyan] is starting...")
    await random_decimal_sleep(0.4, 0.8)

    # Connect to database
    await connect()

    # Now start the bot
    bot_token = db_read("bot_token", ["bot_token:*"])
    TOKEN = bot_token[0][1]
    await bot.start(bot.globals["TOKEN"])

@bot.event
async def on_ready():

    # Check environment variables
    await check_env()

    # Load plugins
    await load_plugins()

    # Start the shell
    await bot.get_cog("TerminalCommands").process_terminal_input()

#################################################################################
# Check for token
#################################################################################
async def check_for_token():

    # Check for the bot token in the database. Can't run without it

    if not table_exists("bot_token"):
        new_db("bot_token", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("bot_token", "TEXT")])

    token_check = db_read("bot_token", ["bot_token:*"])
    
    if not token_check:
        console.print("[bold yellow][?][/bold yellow] What is your bot token? (Clang will not work without this):", end="")
        bot_token = (await ainput(" ")).strip()
        db_insert("bot_token", ["bot_token"], [bot_token])

        print(f"[bold green][✔][/bold green] Token registered successfully.\n")
        await random_decimal_sleep(0.8,1.2)

        return bot_token
    else:
        return token_check[0][1]

#################################################################################
# Connect to database
#################################################################################
async def connect():

    # Database setup

    bot.globals["init_db"] = False

    await random_decimal_sleep(0.4,0.8)
    print(f"[bold cyan]==>[/bold cyan] Connecting to database")
    await random_decimal_sleep(0.1,0.4)

    if not os.path.exists(DB_FILE):
        print(f"[bold cyan]==>[/bold cyan] Database doesn't exist. Creating...")
        await random_decimal_sleep(0.1,0.4)
        try:
            open(DB_FILE, "x").close()
            print(f"[bold cyan]==>[/bold cyan] Database created successfully.")
            await random_decimal_sleep(0.8,1.2)

        except Exception as e:
            print(f"[bold red][X] ERROR:[/bold red] Could not create database: {e}")
            return
            
    print(f"[bold cyan]==>[/bold cyan] Database connection established")
    await random_decimal_sleep(0.8,1.2)

    await check_guilds()


#################################################################################
# Check environment variables
#################################################################################
async def check_env():

    # Check if environment variables exist

    if not table_exists("config"):
        new_db("config", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("command", "TEXT"), ("enabled", "INTEGER")])

    config_check = db_read("config", ["*:*"])
    if not config_check:

        print(f"[bold cyan]==>[/bold cyan] Environment variables not found. Entering setup\n")
        await random_decimal_sleep(0.8,1.2)

        for guild in bot.guilds:
            gid = str(guild.id)
            name = guild.name

            console.print(f"[bold yellow][?][/bold yellow] Setup configuration for {name}? (Y/n): ", end="", highlight=False)
            response = (await ainput("")).strip().lower() or "y"

            if response == "y":
                await setup_guild_config(gid, name)
        
        print("\nSetup complete. Edit the configs at any time by running `config` in the terminal.\n")
        await random_decimal_sleep(0.4,0.8)
    
    else:
        print(f"[bold cyan]==>[/bold cyan] Loaded environment variables\n")
        await random_decimal_sleep(0.1, 0.4)

#################################################################################
# Run the init
#################################################################################
async def ainput(prompt):
    return await asyncio.to_thread(input, prompt)

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

#prompt = "[bold yellow][?][/bold yellow] Sub Mod role ID: "
#submod_role = await get_numeric_input(prompt)

async def setup_guild_config(guild_id, guild_name):

    # Setup questions

    print(f"\n[bold magenta]--- Setup for {guild_name} ---[/bold magenta]\n")

    console.print("[bold yellow][?][/bold yellow] Enable generic commands? Ex: !whois !clang etc (Y/n): ", end="", highlight=False)
    use_generic = (await ainput("")).strip().lower() or "y"

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
        print("[bold cyan]==>[/bold cyan] Creating databases...")
        await random_decimal_sleep(0,0.3)
        if use_cookies == "y":
            new_db("cookies", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("user_id", "TEXT"), ("cookies", "INTEGER")])
        new_db("channelperms", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("name", "TEXT"), ("channelperm", "TEXT")])

        print("[bold cyan]==>[/bold cyan] Databases created. Populating...")
        await random_decimal_sleep(0,0.3)

        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "use_generic", use_generic])
        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "use_mod", use_mod])
        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "use_tickets", use_tickets])
        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "use_logging", use_logging])
        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "use_notes", use_notes])
        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "use_cookies", use_cookies])
        print("[bold green][✔][/bold green] Use flags set.")
        await random_decimal_sleep(0,0.3)

        if use_cookies == "y":
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

        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "submod_enabled", submod_enabled])
        db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "elevation_enabled", elevation_enabled])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "submod_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "mod_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "elev_mod_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "admin_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "elev_admin_role", ""])
        db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "server_owner", ""])
        print("[bold green][✔][/bold green] Roles registered.")
        await random_decimal_sleep(0,0.3)

        print("[bold cyan]==>[/bold cyan] Finalizing...\n") # I know this does nothing but the aesthetics are cool
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
    if existing_guilds:
        for guild_data in existing_guilds:
            # Assuming guild_data[1] is the guild_id column (index 1)
            if guild_data[1] not in current_guild_ids:
                guilds_to_delete.append(guild_data[1])

    # Delete guilds from the database that the bot is no longer part of
    if guilds_to_delete:
        for guild_id in guilds_to_delete:
            db_delete("guilds", [f"guild_id:{guild_id}"])
            print(f"[bold cyan]==>[/bold cyan] Deleted guild {guild_id} from the database. Clang is no longer there.")

    # Update the database with any new guilds
    for guild in bot.guilds:
        guild_data = [guild.name, str(guild.id)]
        
        existing_guild = db_read("guilds", [f"guild_id:{guild.id}"])

        if not existing_guild:
            db_insert("guilds", ["guild_name", "guild_id"], guild_data)
            print(f'Added guild "{guild.name}" to the database. ({guild.id}).')

        bot.globals["guilds"].append([guild.name, str(guild.id)])
        
    for guild in bot.guilds:
        print(f"[bold cyan]==>[/bold cyan] Clang exists in {guild.name} ({guild.id}).")
        await random_decimal_sleep(0.1, 0.3)

#################################################################################
# Load plugins
#################################################################################
async def load_plugins():

    # Search all plugins in /plugins and gracefully fail on any errors

    for filename in os.listdir("./plugins"):
        if filename.endswith(".py"):
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
        print("[bold red]Clang is alive.[/bold red] (Hint: run `help`)\n")
    else:
        print(f"[bold red]Clang is awake.[/bold red] (Hint: run 'help')\n")
    
    await random_decimal_sleep(0.4, 0.8)

# Run the bot
asyncio.run(start_bot())