import discord
import os
import asyncio
import time
import random
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from discord.ext import commands
from db import init_db, db_create, db_read, db_update

load_dotenv()

version = "0.2"

activity = discord.Game(name="!help")

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("No token found in the .env file!")
    time.sleep(0.5)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", activity=activity, help_command=None, intents=intents)

# Initialize the database
init_db()

# Custom async function to sleep for a random decimal between min_sleep and max_sleep
async def random_decimal_sleep(min_sleep, max_sleep):
    sleep_time = random.uniform(min_sleep, max_sleep)  # Generate a random float between min_sleep and max_sleep
    await asyncio.sleep(sleep_time)

# Function to load plugins
async def load_plugins():
    db_needs_init = False

    print("__________________________________________________________________________\n")
    await random_decimal_sleep(0.1, 0.6)
    print("Cosmic Arp © 2025 - maidnaut@gnamil.com\n\n")

    print('''     √√√√∞√√√≈÷      
  ×√√≈√√√√√√√  √     
+×+××≠√√    √√       
 ≈+××√√√    √√×≠∞    
×≈√ √√√√√√÷√√√≈≈√√   
 ×≈≈√≠∞√-√ ∞√√√      
  ≈√√√= √≈           
    √√√√≈÷√  ××√√√√  
           ××××××  ×\n''')

    await random_decimal_sleep(0.1, 0.6)
    print("__________________________________________________________________________\n")
    await random_decimal_sleep(0.1, 0.4)
    print(f"\nClang v{version} is starting...\n")
    await random_decimal_sleep(0.5,1)

    print(f"Connecting to database")
    await random_decimal_sleep(0.1,0.4)

    DB_FILE = 'bot_data.db'

    if not os.path.exists(DB_FILE):
        print(f"Database doesn't exist. Creating...")
        await random_decimal_sleep(0.1,0.4)
        try:
            open(DB_FILE, "x").close()
            db_needs_init = True
        except Exception as e:
            print(f"\nERROR: Could not create database: {e}")
            return
    else:
        # Check if configs table exists
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='configs';")
            table_exists = cursor.fetchone()
            conn.close()
            if not table_exists:
                db_needs_init = True
        except Exception as e:
            print(f"\nERROR checking table existence: {e}")
            return

    if db_needs_init:
        print("Initializing database schema...")
        await random_decimal_sleep(0.1,0.4)
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    enabled TEXT NOT NULL
                );
            ''')
            conn.commit()
            conn.close()
            print("Database initialized successfully.")
            await random_decimal_sleep(0.1,0.4)
        except Exception as e:
            print(f"\nERROR initializing database: {e}")
            return
    
    print(f"Database connection established")
    await random_decimal_sleep(0.8,1.2)
    
    print(f"Loaded environment variables")
    await random_decimal_sleep(0.1, 0.4)

    for filename in os.listdir("./plugins"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"plugins.{filename[:-3]}")
                print(f"Loaded plugin/{filename}")
                await random_decimal_sleep(0.1, 0.4)
            except Exception as e:
                print(f"Failed to load plugin {filename}: {e}")
                await random_decimal_sleep(0.1, 0.4)
    print("\n")

    await random_decimal_sleep(0.8, 1.2)

    if db_needs_init:
        print("Clang is alive. (Hint: run `help`)\n")
    else:
        print(f"Clang is awake. (Hint: run 'help')\n")

# Function to start bot and load plugins
async def start_bot():
    # Load plugins first
    await load_plugins()

    # Now start the bot
    await bot.start(TOKEN)

@bot.event
async def on_ready():

    await bot.get_cog("TerminalCommands").process_terminal_input()  # Start the terminal command loop

# Run the bot
asyncio.run(start_bot())
