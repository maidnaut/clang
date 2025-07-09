import os, sys, time, random, asyncio, discord
from inc.db import *
from pathlib import Path
from discord.ext import commands, tasks
from rich.console import Console
from inc.utils import *

version = "0.9b"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    TOKEN = loop.run_until_complete(check_for_token())
finally:
    pass


class ClangBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.globals = {}
        self.avatar_paths = []
        self.status_messages = [
            "discord.gg/cli-cafe",
            "!help",
            "CLANG 👏 CLANG 👏 CLANG 👏",
            "No maidens?",
            "i use arch btw",
            "install gentoo",
            "aaaaaAAAAA????",
            "https://github.com/maidnaut/clang",
            "The virtual plaza welcomes you",
            "Present day, present time",
            "Let's all love Lain",
            "Despite everything, it's still you",
            "Pasting ￼ in a dangerous neighborhood",
            "Pronouns: any/all",
            "Coping with Navis",
            "Red is not blue",
            "Welcome to nowhere",
            "sudo rm -rf /skull",
            "Ping: ∞ms",
            "🍌 Banana for scale",
            "KERNEL PANIC",
            "AAAAAAAAAAAAAAAAA",
            "NO NO NO NO NO",
            "WHAT'S THE WIFI PASSWORD???",
            "💀",
        ]

    # Status Change
    @tasks.loop(seconds=3900)
    async def random_status(self):
        new_status = random.choice(self.status_messages)
        await self.change_presence(activity=discord.Game(name=new_status))
    @random_status.before_loop
    async def before_random_status(self):
        await self.wait_until_ready()

    # Avatar change
    @tasks.loop(seconds=18000)
    async def random_avatar(self):
        if self.avatar_paths:
            avatar_path = random.choice(self.avatar_paths)
            try:
                with open(avatar_path, 'rb') as f:
                    avatar_bytes = f.read()
                await self.user.edit(avatar=avatar_bytes)
            except Exception as e:
                print(f"[bold red]Error changing avatar: {e}[/bold red]")
    @random_avatar.before_loop
    async def before_random_avatar(self):
        await self.wait_until_ready()

# Pycord stuff
activity = discord.Game(name="Restarting...")
bot = ClangBot(
    command_prefix="!",
    activity=activity,
    help_command=None,
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions.none()
)

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
    print("[bold red]Cosmic Arp © 2025[/bold red] - maidnaut@gmail.com\n\n")
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

    await connect()

    await bot.start(bot.globals["TOKEN"])

@bot.event
async def on_ready():

    # Check guilds
    await check_guilds()

    # Check environment variables
    await check_env()

    # Load plugins
    print("[bold cyan]==>[/bold cyan] Loading plugins...", highlight=False)
    await random_decimal_sleep(0.1, 0.4)
    print("\n")

    await load_plugins()

    # Sync the slash commands
    synced = True
    for guild in bot.guilds:
        try:
            await bot.sync_commands(guild_ids=[guild.id])

        except discord.Forbidden:
            print(f"[bold red][X][/bold red] Missing permissions to sync commands for {guild.name} ({guild.id}).")
            await random_decimal_sleep(0.1, 0.4)   
            synced = False

        except discord.HTTPException as e:
            print(f"[bold red][X][/bold red] HTTP error while syncing for {guild.name} ({guild.id}): {e}")
            await random_decimal_sleep(0.1, 0.4)   
            synced = False

        except discord.ClientException as e:
            print(f"[bold red][X][/bold red] Client error during sync for {guild.name} ({guild.id}): {e}")
            await random_decimal_sleep(0.1, 0.4)   
            synced = False

    if synced:
        print(f"[bold green][✔][/bold green] Synced slash commands to all servers")
        await random_decimal_sleep(0.1, 0.4)


    print("\n")

    # Good morning Clang
    if bot.globals["init_db"]:
        print("Clang is alive. (Hint: run `help`)\n")
    else:
        print(f"Clang is awake. (Hint: run 'help')\n")

    await random_decimal_sleep(0.1, 0.4)

    # Default status
    await bot.change_presence(activity=discord.Game(name="!help"))
    bot.random_status.start()

    # Load avatar paths
    avatar_dir = Path("avatars")
    avatar_dir.mkdir(exist_ok=True)
    bot.avatar_paths = [
        f for f in avatar_dir.glob("*")
        if f.is_file() and f.suffix.lower() in [".png", ".jpg", ".jpeg"]
    ]
    
    if bot.avatar_paths:
        bot.random_avatar.start()
    else:
        print("[bold yellow]No avatars found in 'avatars' directory[/bold yellow]")
    
#################################################################################
# Connect to database
#################################################################################
async def connect():
    # Database setup

    await random_decimal_sleep(0.4, 0.8)
    print(f"[bold cyan]==>[/bold cyan] Connecting to database")
    await random_decimal_sleep(0.1, 0.4)

    if not os.path.exists(DB_FILE):
        print(f"[bold cyan]==>[/bold cyan] Database doesn't exist. Creating...", highlight=False)
        await random_decimal_sleep(0.1, 0.4)
        try:
            open(DB_FILE, "x").close()
            print(f"[bold cyan]==>[/bold cyan] Database created successfully.")
            await random_decimal_sleep(0.8, 1.2)

        except PermissionError:
            print(f"[bold red][X] ERROR:[/bold red] Permission denied while creating database.")
            return

        except OSError as e:
            print(f"[bold red][X] ERROR:[/bold red] OS error while creating database: {e}")
            return
            
    print(f"[bold cyan]==>[/bold cyan] Database connection established")
    await random_decimal_sleep(0.4, 0.8)

#################################################################################
# Check environment variables
#################################################################################

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
        await random_decimal_sleep(0.8, 1.2)

        PLUGINS = {}
        def register_plugins(name: str, func: callable):
            PLUGINS[name] = func

        for guild in bot.guilds:
            gid = str(guild.id)
            name = guild.name
            await install(gid, name)
        
        print("\nSetup complete.\n")
        await random_decimal_sleep(0.4, 0.8)
    
    else:
        print(f"[bold cyan]==>[/bold cyan] Loaded environment variables")
        await random_decimal_sleep(0.1, 0.4)

#################################################################################
# Run the init
#################################################################################

async def install(guild_id, guild_name):

    # Setup questions

    print(f"[bold cyan]==>[/bold cyan] Setting up {guild_name}...")


    # Do a whole bunch of stuff to set up the db here

    try:
        print("[bold cyan]==>[/bold cyan] Creating databases...", highlight=False)
        await random_decimal_sleep(0, 0.3)
        new_db("logchans", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("name", "TEXT"), ("channel", "TEXT")])
        new_db("commands", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("name", "TEXT"), ("enabled", "TEXT")])
        new_db("cookies", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("user_id", "TEXT"), ("cookies", "INTEGER")])
        new_db("cookie_rate", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("rate", "INTEGER")])
        new_db("roles", [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), ("guild_id", "TEXT"), ("name", "TEXT"), ("role", "TEXT")])

        print("[bold cyan]==>[/bold cyan] Databases created. Populating...", highlight=False)
        await random_decimal_sleep(0, 0.3)

        db_insert("cookie_rate", ["guild_id", "rate"], [guild_id, 100])
        print("[bold green][✔][/bold green] Default random chance of cookie drops set to 1 in 100 messages.")
        await random_decimal_sleep(0, 0.3)

        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "joinlog", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "modlog", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "logs", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "botlogs", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "ticketlog", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "jaillog", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "ticket_category", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "jail_category", ""])
        db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, "mod_category", ""])
        print("[bold green][✔][/bold green] Channels registered.")
        await random_decimal_sleep(0, 0.3)

        db_insert("config", ["guild_id", "name", "enabled"], [guild_id, "elevation_enabled", "y"])

        db_insert("roles", ["guild_id", "name", "role"], [guild_id, "jail", ""])
        db_insert("roles", ["guild_id", "name", "role"], [guild_id, "submod", ""])
        db_insert("roles", ["guild_id", "name", "role"], [guild_id, "mod", ""])
        db_insert("roles", ["guild_id", "name", "role"], [guild_id, "op", ""])
        db_insert("roles", ["guild_id", "name", "role"], [guild_id, "admin", ""])
        db_insert("roles", ["guild_id", "name", "role"], [guild_id, "root", ""])
        db_insert("roles", ["guild_id", "name", "role"], [guild_id, "bots", ""])
        print("[bold green][✔][/bold green] Roles registered.")
        await random_decimal_sleep(0, 0.3)

        print(f"[bold green][✔][/bold green] Use flags for {guild_name} set.\n")
        await random_decimal_sleep(0, 0.3)

        bot.globals["init_db"] = True

    except sqlite3.IntegrityError as e:
        print(f"[bold red][X][/bold red] Integrity error: {e}")
        return

    except sqlite3.OperationalError as e:
        print(f"[bold red][X][/bold red] Operational error: {e}")
        return

    except sqlite3.ProgrammingError as e:
        print(f"[bold red][X][/bold red] Programming error: {e}")
        return

    except sqlite3.DatabaseError as e:
        print(f"[bold red][X][/bold red] General database error: {e}")
        return

    except (TypeError, ValueError) as e:
        print(f"[bold red][X][/bold red] Invalid data passed to db functions: {e}")
        return

#################################################################################
# Check for guilds
#################################################################################
async def check_guilds():
    
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

            except discord.NoEntryPointError:
                print(f"[bold red][X][/bold red] Plugin {filename} missing setup() function.")
                await random_decimal_sleep(0, 0.4)

            except discord.ExtensionFailed as e:
                print(f"[bold red][X][/bold red] Plugin {filename} raised an error during setup: {e}")
                await random_decimal_sleep(0, 0.4)

            except discord.ExtensionError as e:
                print(f"[bold red][X][/bold red] Extension error in plugin {filename}: {e}")
                await random_decimal_sleep(0, 0.4)
                
    await random_decimal_sleep(0.8, 1.2)

#################################################################################
# Main loop
#################################################################################

if __name__ == "__main__":
    loop.run_until_complete(start_bot())

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        raise error
