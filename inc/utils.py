import discord, random, asyncio, sys, re
from inc.db import *
from rich.console import Console
from discord.ext import commands
from discord.ext.commands import CommandNotFound

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

# Get the token
async def check_for_token():
    env = get_data_path() / ".env"
    if not env.exists():
        env.write_text("", encoding="utf-8")

    while True:
        text = env.read_text(encoding="utf-8")
        m = re.search(r"^BOT_TOKEN\s*=\s*([\w\-\.]{59,72})\s*$", text, re.MULTILINE)

        if m:
            token = m.group(1).strip()
            if token.count('.') == 2 and 59 <= len(token) <= 72:
                return token
            else:
                print(f"[!] Invalid token structure: {token} (length: {len(token)})")

        if sys.stdin.isatty():
            print("[?] Enter bot token: ", end="")
            token = (await asyncio.get_event_loop()
                    .run_in_executor(None, input, "")).strip()

            env.write_text(f"BOT_TOKEN={token}\n", encoding="utf-8")
            print("[✔] Token saved")
            return token

        print("[!] Waiting for valid token in .env...")
        await asyncio.sleep(5)

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

# Get role level
async def get_level(ctx):
    role_levels = {
        "everyone": 0,
        "submod": 1,
        "mod": 2,
        "op": 3,
        "admin": 4,
        "root": 5,
    }

    roles = {}
    role_list = db_read("roles", [f"guild_id:{ctx.guild.id}", "role:*"])
    for row in role_list:
        name_col, id_col = row[2], row[3]
        if id_col:
            roles[name_col] = int(id_col)

    author_roles = [r.id for r in ctx.author.roles]

    highest = 0
    for name, r_id in roles.items():
        if r_id in author_roles and name in role_levels:
            level = role_levels[name]
            if level > highest:
                highest = level

    elevation = db_read("config", [f"guild_id:{ctx.guild.id}", "name:elevation_enabled"])
    if elevation and elevation[0][0] == "n":
        if highest == 2: highest = 3
        if highest == 4: highest = 5

    return highest

# get targets level
async def get_target_level(guild, member):
    role_levels = {
        "everyone": 0,
        "submod": 1,
        "mod": 2,
        "op": 3,
        "admin": 4,
        "root": 5,
    }

    roles = {}
    role_list = db_read("roles", [f"guild_id:{guild.id}", "role:*"])
    for row in role_list:
        name_col, id_col = row[2], row[3]
        if id_col:
            roles[name_col] = int(id_col)

    author_roles = [r.id for r in member.roles]

    highest = 0
    for name, r_id in roles.items():
        if r_id in author_roles and name in role_levels:
            level = role_levels[name]
            if level > highest:
                highest = level

    elevation = db_read("config", [f"guild_id:{guild.id}", "name:elevation_enabled"])
    if elevation and elevation[0][0] == "n":
        if highest == 2: highest = 3
        if highest == 4: highest = 5

    return highest

async def has_perms(ctx):
    try:
        elevation_config = db_read("config", [
            f"guild_id:{ctx.guild.id}", 
            "name:elevation_enabled"
        ])
        
        if elevation_config:
            elevation_enabled = elevation_config[0][3].lower()

        roles = {}
        role_list = db_read("roles", [f"guild_id:{ctx.guild.id}", "role:*"])
        for row in role_list:
            name_col, id_col = row[2], row[3]
            if id_col:
                roles[name_col] = int(id_col)

        user_roles = {role.id for role in ctx.author.roles}

        if elevation_enabled == "y":
            if roles.get("submod") in user_roles or roles.get("op") in user_roles or roles.get("root") in user_roles:
                return True
            
            if "mod" in roles or "admin" in roles:
                await ctx.send("!op?")
            
            return False

        else:
            if roles.get("submod") in user_roles or roles.get("mod") in user_roles or roles.get("admin") in user_roles:
                return True
            
            await ctx.send("You need mod privileges for this command")
            return False

    except Exception as e:
        await ctx.send(f"Permission check error: {e}")
        return False

# Global user search
async def get_user(ctx, user_id):
    user = "N/A"
    try:
        # First try as member
        user = await commands.MemberConverter().convert(ctx, user_id)
    except commands.MemberNotFound:
        try:
            # Then try as global user
            user = await commands.UserConverter().convert(ctx, user_id)
        except commands.UserNotFound:
            user = "N/A"
            return

    return user

# Check ping status
async def author_ping(ctx):

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    check_row = db_read("pings", [f"guild_id:{guild_id}", f"user_id:{user_id}"])

    ping = True
    if check_row:
        if check_row[0][3] == "on":
            ping = True
        else:
            ping = False
    
    if ping == True:
        return f"{ctx.author.mention}"
    else:
        return f"{ctx.author.display_name}"

# Check ping status
async def user_ping(ctx, user):

    user_id = user.id
    guild_id = ctx.guild.id
    check_row = db_read("pings", [f"guild_id:{guild_id}", f"user_id:{user_id}"])

    ping = True
    if check_row:
        if check_row[0][3] == "on":
            ping = True
        else:
            ping = False
    
    if ping == True:
        return f"{user.mention} "
    else:
        return f"{user.display_name}"

# Check ping status
async def check_ping(ctx, user):

    user_id = user.id
    guild_id = ctx.guild.id
    check_row = db_read("pings", [f"guild_id:{guild_id}", f"user_id:{user_id}"])

    ping = True
    if check_row:
        if check_row[0][3] == "on":
            ping = True
        else:
            ping = False
    
    if ping == True:
        return f"{user.mention} "
    else:
        return f"{user.display_name}"

# Check ping status
async def check_ping_id(ctx, user_id: str):

    user_id = user_id
    guild_id = ctx.guild.id
    check_row = db_read("pings", [f"guild_id:{guild_id}", f"user_id:{user_id}"])

    ping = True
    if check_row:
        if check_row[0][3] == "on":
            ping = True
        else:
            ping = False

    try:
        # First try as member
        user = await commands.MemberConverter().convert(ctx, user_id)
    except commands.MemberNotFound:
        try:
            # Then try as global user
            user = await commands.UserConverter().convert(ctx, user_id)
        except commands.UserNotFound:
            return "N/A"
    
    if ping == True:
        return f"{user.mention} "
    else:
        return f"{user.display_name}"

# Get channels
async def get_channel(guild_id, name):
    try:
        settings = db_read("logchans", [f"guild_id:{guild_id}", f"name:{name}"])
        if not settings or not settings[0][3]:
            return None
        
        channel_id = int(settings[0][3])
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return None
        
        channel = guild.get_channel(channel_id)
        if not channel:
            try:
                channel = await guild.fetch_channel(channel_id)
            except discord.NotFound:
                return None
        
        return channel
    except Exception as e:
        return None
