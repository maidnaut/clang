import discord
import os
from discord.ext import commands
from permissions import has_elevated_permissions

# Elevated permission roles
MODERATOR_ROLE = int(os.getenv("moderatorRole"))
ADMIN_ROLE = int(os.getenv("adminRole"))
OPERATOR_ROLE = int(os.getenv("operatorRole"))
ROOT_ROLE = int(os.getenv("rootRole"))

class OpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Help info
        self.__help__ = {
            "op": {
                "args": "",
                "desc": "Grants elevated perms. Must always be activated to mute and ban",
                "perm": ["mod", "admin"]
            }
        }

    @commands.command()
    async def op(self, ctx):

        user = ctx.author

        # Logic to assign or remove roles
        user_roles = [role.id for role in user.roles]

        if MODERATOR_ROLE in user_roles:
            target_role = OPERATOR_ROLE
            role_name = "Operator"
        elif ADMIN_ROLE in user_roles:
            target_role = ROOT_ROLE
            role_name = "Root"
        else:
            await ctx.send("You do not have the necessary role to use this command.")
            return

        target_role_obj = discord.utils.get(ctx.guild.roles, id=target_role)

        if target_role_obj in user.roles:
            await user.remove_roles(target_role_obj)
            await ctx.send(f"{user.name} put their gun away.")
        else:
            await user.add_roles(target_role_obj)
            await ctx.send(f"Oh shit {user.name}'s got their gun out.")

def setup(bot):
    bot.add_cog(OpCog(bot))
