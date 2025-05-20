import discord
from discord.ext import commands, tasks
from inc.utils import *




def setup(bot):
    bot.add_cog(SettingsCog(bot))



class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.__help__ = {
            "setping": {
                "args": "on, off",
                "desc": "Enables or disables ping responses from Clang",
                "perm": ["everyone"]
            },
        }

        if not table_exists("pings"):
            new_db("pings", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER"),
                ("user_id", "INTEGER"),
                ("status", "TEXT"),
            ])




    # check for how to update the db
    async def update(self, guild_id, author, name, value, row_type):

        try:
            if row_type == "role":
                check_row = db_read("roles", [f"guild_id:{guild_id}", f"name:{name}"])
            elif row_type == "channel":
                check_row = db_read("logchans", [f"guild_id:{guild_id}", f"name:{name}"])
            
            if not result:
                if row_type == "role":
                    db_insert("roles", ["guild_id", "name", "role"], [guild_id, name, value])
                    return f"{author.mention} {name} role set!"
                elif row_type == "channel":
                    db_insert("logchans", ["guild_id", "name", "channel"], [guild_id, name, value])
                    return await ctx.send(f"{author.mention} {name} channel/category set!")

            else:
                if row_type == "roles":
                    db_update("roles", [f"guild_id:{guild_id}", f"name:{name}"], [("role", value)])
                    return await ctx.send(f"{author.mention} {name} role set!")
                elif row_type == "channel":
                    db_update("logchans", [f"guild_id:{guild_id}", f"name:{name}"], [("channel", value)])
                    return await ctx.send(f"{author.mention} {name} channel/category set!")

        except Exception as e:
            await ctx.send(f"Database error: {e}")




    # toggle pings
    @commands.command()
    async def setping(self, ctx, status: str = None):

        guild_id = ctx.guild.id
        user_id = ctx.user.id

        if status == None:
            return await ctx.send(f"{check_pings(ctx)}Please supply a valid argument: `!ping [on, off]`")

        options = ["on", "off"]
        if status not in options:
            return await ctx.send(f"{check_pings(ctx)}Please supply a valid argument: `!ping [on, off]`")

        check_row = db_read("pings", [f"guild_id:{guild_id}", f"user_id:{user_id}"])

        if not result:
            db_insert("pings", ["guild_id", "user_id", "status"], [guild_id, user_id, status])
        else:
            db_update("pings", [f"guild_id:{guild_id}", f"user_id:{user_id}"], [("status", status)])

        return await ctx.send(f"{check_pings(ctx)}Ping status set to `{status}`")




    # !elevation command
    @commands.command()
    async def elevation(self, ctx, status: str = None):
        
        user_level = await get_level(ctx)
        guild_id = ctx.guild.id
        author = ctx.author
        owner = ctx.guild.owner

        if user_level >= 4 or author == owner:
            if status == "on":
                db_update("config", [f"guild_id:{guild_id}", f"name:elevation_enabled"], [("enabled", "y")])
                await ctx.send(f"{check_pings(ctx)} !op is now required on this server.")
            if status == "off":
                db_update("config", [f"guild_id:{guild_id}", f"name:elevation_enabled"], [("enabled", "n")])
                await ctx.send(f"{check_pings(ctx)} !op is now disabled on this server.")





    # !setrole command
    @commands.command()
    async def setrole(self, ctx, role: str = None, *, id: str = None):
        
        user_level = await get_level(ctx)
        author = ctx.author
        guild_id = ctx.guild.id
        owner = ctx.guild.owner

        if user_level >= 4 or author == owner:

            roles = [
                "jail",
                "submod",
                "mod",
                "op",
                "admin",
                "root",
                "bots"
            ]

            all_roles = ", ".join(roles)

            if not role:
                await ctx.send(f"{check_pings(ctx)} Please select a role: `{all_roles}` \n-# !setrole <role> <id>")
                return
            
            if not id:
                await ctx.send(f"{check_pings(ctx)} Please provide an ID \n-# !setrole <role> <id>")
                return

            if role not in roles:
                await ctx.send(f"{check_pings(ctx)} Please select a valid role: `{all_roles}` \n-# !setrole <role> <id>")
                return

            if not id.isdigit():
                await ctx.send(f"{check_pings(ctx)} Please provide a valid role ID \n-# !setrole <rold> <id>")
                return

            await update(self, guild_id, author, role, id, "role")




    # !setchannel command
    @commands.command()
    async def setchannel(self, ctx, channel: str = None, *, id: str = None):

        user_level = await get_level(ctx)
        author = ctx.author
        guild_id = ctx.guild.id
        owner = ctx.guild.owner

        if user_level >= 4 or author == owner:

            channels = [
                "joinlog",
                "modlog",
                "logs",
                "botlogs",
                "ticketlog",
                "jaillog",
                "ticket_category",
                "jail_category",
                "mod_category"
            ]

            all_channels = ", ".join(channels)

            if not channel:
                await ctx.send(f"{check_pings(ctx)} Please select a channel or category: `{all_channels}` \n-# !setchannel <channel> <id>")
                return
            
            if not id:
                await ctx.send(f"{check_pings(ctx)} Please provide an ID \n-# !setchannel <channel> <id>")
                return

            if channel not in channels:
                await ctx.send(f"{check_pings(ctx)} Please select a valid channel or category: `{all_channels}` \n-# !setchannel <channel> <id>")
                return

            if not id.isdigit():
                await ctx.send(f"{check_pings(ctx)} Please provide a valid channel or category ID \n-# !setchannel <channel> <id>")
                return


            await update(self, guild_id, author, role, id, "channel")