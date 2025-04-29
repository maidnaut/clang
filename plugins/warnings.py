import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv
from permissions import has_elevated_permissions

# Load env vars
load_dotenv()
def get_int_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Missing {var_name} in .env file")
    return int(value)

MODERATOR_ROLE = get_int_env_var("moderatorRole")
ADMIN_ROLE = get_int_env_var("adminRole")
OPERATOR_ROLE = get_int_env_var("operatorRole")
ROOT_ROLE = get_int_env_var("rootRole")

DB_FILE = 'bot_data.db'

# Create database if it doesn't exist
def ensure_warnings_table_exists():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            author_id TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

class WarningsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_warnings_table_exists()
    
    @commands.command()
    async def warn(self, ctx, user: str = None, *, reason: str = None):
        if user is None and reason is None:
            await ctx.send("To warn someone, run ``!warn <@user/id> (reason)``")
            return

        if not (user.startswith("<@") and user.endswith(">")) and not user.isdigit():
            await ctx.send("Invalid warn format. ``!warn <@user/id> (reason)``")
            return

        if user.isdigit() and not (17 <= len(user) <= 20):
            await ctx.send("Invalid user id format. User IDs must be 17 to 20 digits long.")
            return

        if reason is None:
            await ctx.send("Warnings require a reason. `!warn <@user/id> (reason)`")
            return

        if user.startswith("<@") and user.endswith(">"):
            user_id = user.strip("<@!>")
        else:
            user_id = user

        member = ctx.guild.get_member(int(user_id))
        mod_id = str(ctx.author.id)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute('SELECT note_id FROM warnings WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
        row = c.fetchone()
        if row:
            note_id = int(row[0]) + 1
        else:
            note_id = 1

        c.execute('''
            INSERT INTO warnings (note_id, user_id, date, author_id, reason)
            VALUES (?, ?, datetime('now'), ?, ?)
        ''', (note_id, user_id, mod_id, reason))

        conn.commit()
        conn.close()

        mention_text = member.mention if member else f"<@{user_id}>"
        await ctx.send(f"Warned {mention_text} for reason: {reason}")



# Initialize cog
def setup(bot):
    bot.add_cog(WarningsCog(bot))