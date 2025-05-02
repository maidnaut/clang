import discord
import os
from inc.db import *

async def has_elevated_permissions(ctx):


    db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "submod_enabled", submod_enabled])
    db_insert("config", ["guild_id", "command", "enabled"], [guild_id, "elevation_enabled", elevation_enabled])
    db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "submod_role", ""])
    db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "mod_role", ""])
    db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "elev_mod_role", ""])
    db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "admin_role", ""])
    db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "elev_admin_role", ""])
    db_insert("channelperms", ["guild_id", "name", "channelperm"], [guild_id, "server_owner", ""])

    elevation_config = db_read("config", [f"guild:{ctx.guild.id}", "elevation_enabled:*"])
    elevation_enabled = elevation_config[0][1]

    roles = db_read("channelperms", [f"guild:{ctx.guild.id}", "*:*"])

    mod = roles[0][2]
    op = roles[0][3]
    admin = roles[0][4]
    root = roles[0][5]
    owner = roles[0][6]

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