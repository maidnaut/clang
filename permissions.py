# permissions.py

import discord
from dotenv import load_dotenv
import os

load_dotenv()

# Elevated permission roles (for example: moderator, admin, operator)
MODERATOR_ROLE = int(os.getenv("moderatorRole"))
ADMIN_ROLE = int(os.getenv("adminRole"))
OPERATOR_ROLE = int(os.getenv("operatorRole"))
ROOT_ROLE = int(os.getenv("rootRole"))

# Refactor has_elevated_permissions to be async
async def has_elevated_permissions(ctx):
    if any(role.id in [OPERATOR_ROLE, ROOT_ROLE] for role in ctx.author.roles):
        return True
    else:
        await ctx.send("!op?")
        return False
