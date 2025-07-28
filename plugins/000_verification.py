import datetime, discord
from inc.utils import *
from discord.ext import commands, tasks

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
        
        if not table_exists("to_be_verified"):
            new_db("to_be_verified", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER"),
                ("user_id", "INTEGER"),
                ("time", "STRING")
            ])

        if not self.verification_loop.is_running():
            self.verification_loop.start()

    @commands.command()
    async def verificationtime(self, ctx, time: str = None):
        user_level = await get_level(ctx)
        author = ctx.author
        owner = ctx.guild.owner

        if user_level <= 3 and author != owner:
            return

        if time is None:
            await ctx.send(f"{await author_ping(ctx)} Please provide a time. ``!verificationtime <time>``" )
            return

        # Time is an int, interpret as seconds
        if time.isdigit():
            time = int(time)
            db_update("verification_time", [f"guild_id:{ctx.guild.id}"], [("time", time)])
            await ctx.send(f"{await author_ping(ctx)} Verification time set to {time} second(s).")
            return
        
        match = re.match(r"^(\d+)([smhdwMy])$", time.strip().lower())
        if not match:
            await ctx.send(f"{await author_ping(ctx)} Invalid format. Use like ``!slowmode 10s``, ``5m``, or ``1h``.")
            return
        
        value, unit = match.groups()
        value = int(value)

        durations = [('s', 1, f"{value} second(s)"), ('m', 60, f"{value} minute(s)"), ('h', 60, f"{value} hour(s)"), ('d', 24, f"{value} day(s)"), ('w', 7, f"{value} week(s)"), ('M', 4, f"{value} month(s)"), ('y', 12, f"{value} year(s)")]

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

        verification_time = (datetime.datetime.now() + datetime.timedelta(seconds=time)).replace(microsecond=0).isoformat()

        to_be_verified = db_read("to_be_verified", [f"guild_id:{member.guild.id}", f"user_id:{member.id}"])
        if to_be_verified == []:
            db_insert("to_be_verified", ["guild_id", "user_id", "time"], [member.guild.id, member.id, verification_time])
        else:
            db_update("to_be_verified", [f"guild_id:{member.guild.id}", f"user_id:{member.id}"], [("time", verification_time)])
    
    @tasks.loop(minutes=1)
    async def verification_loop(self):
        cur_time = datetime.datetime.now().replace(microsecond=0).isoformat()

        to_be_verified = db_read("to_be_verified", [f"time:<{cur_time}"])
        for row in to_be_verified:
            guild_id = int(row[1]); user_id = int(row[2]); time = row[3]
            guild    = discord.utils.get(self.bot.guilds, id=guild_id)
            if not guild:
                continue

            user = guild.get_member(user_id)
            role_id = int(db_read("roles", [f"guild_id:{guild_id}", "name:verified"])[0][3])
            try:
                await user.add_roles(discord.Object(id=role_id), reason="Verification")
            except Exception as e:
                print(f"\n[!] Verification failed for {user_id}@{guild_id}: {e}")

            db_remove("to_be_verified", ["guild_id", "user_id"], [guild.id, user_id])
