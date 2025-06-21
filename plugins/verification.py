import discord
from inc.utils import *
from discord.ext import commands

def setup(bot):
    bot.add_cog(VerificationCog(bot))


class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.__help__ = {
            "verificationtime": {
                "args": "<time>",
                "desc": "Time it takes for users to get the verified role",
                "perm": ["mod", "admin"]
            }
        }

        if not table_exists("verification_time"):
            new_db("verification_time", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER"),
                ("time", "INTEGER")
            ])

    @commands.command()
    async def verificationtime(self, ctx, time: str = None):
        user_level = await get_level(ctx)
        author = ctx.author
        owner = ctx.guild.owner

        if user_level <= 3 and author != owner:
            return

        if time is None:
            await ctx.send(f"{await author_ping(ctx)} Please provide a time. ``!verificationtime <time>``" )

        # Time is an int, interpret as seconds
        if time.isdigit():
            time = int(time)
            db_update("verification_time", [f"guild_id:{ctx.guild.id}"], [("time", time)])
            await ctx.send(f"{await author_ping(ctx)} Verification time set to {time} second(s).")
            return
        
        match = re.match(r"^(\d+)([smhdw])$", time.strip().lower())
        if not match:
            return await ctx.send(f"{await author_ping(ctx)} Invalid format. Use like ``!slowmode 10s``, ``5m``, or ``1h``.")
        
        value, unit = match.groups()
        value = int(value)

        durations = [('s', 1, f"{value} second(s)"), ('m', 60, f"{value} minute(s)"), ('h', 60, f"{value} hour(s)"), ('d', 24, f"{value} day(s)"), ('w', 7, f"{value} week(s)")]

        seconds = value
        for duration in durations:
            seconds *= duration[1]
            if unit == duration[0]:
                display = duration[2]
                break

        if seconds <= 0:
            await ctx.send(f"{await author_ping(ctx)} Rate too low! Must be above 0 seconds.")
            return
        
        row_exist = db_read("verification_time", [f"guild_id:{ctx.guild.id}"])
        if len(row_exist) == 0:
            db_insert("verification_time", ["guild_id", "time"], [ctx.guild.id, seconds])
        else:
            db_update("verification_time", [f"guild_id:{ctx.guild.id}"], [("time", seconds)])

        await ctx.send(f"{await author_ping(ctx)} Verification time set to {display}.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role_id = db_read("roles", [f"guild_id:{member.guild.id}", "name:verified"])
        time = db_read("verification_time", [f"guild_id:{member.guild.id}"])

        if time == [] or role_id == []:
            return
        
        time = time[0][2]
        role_id = role_id[0][3]

        asyncio.create_task(self._verify_after_timeout(member, time, role_id))

    async def _verify_after_timeout(self, member, time, role_id):
        await asyncio.sleep(time)

        if member.guild.get_role(role_id) in member.roles:
            return
        
        if not member.guild:
            return

        await member.add_roles(discord.Object(role_id))
