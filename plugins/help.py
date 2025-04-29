import discord
import os
from discord.ext import commands

# Elevated permission roles
ALUMNI_ROLE = int(os.getenv("alumniRole"))
MODERATOR_ROLE = int(os.getenv("moderatorRole"))
ADMIN_ROLE = int(os.getenv("adminRole"))
OPERATOR_ROLE = int(os.getenv("operatorRole"))
ROOT_ROLE = int(os.getenv("rootRole"))

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        author_roles = [role.id for role in ctx.author.roles]

        def get_level():
            if ROOT_ROLE in author_roles:
                return "root"
            elif OPERATOR_ROLE in author_roles:
                return "op"
            elif ADMIN_ROLE in author_roles:
                return "admin"
            elif MODERATOR_ROLE in author_roles:
                return "mod"
            elif ALUMNI_ROLE in author_roles:
                return "alumni"
            return "everyone"

        ROLE_LEVELS = {
            "everyone": 0,
            "alumni": 1,
            "mod": 2,
            "admin": 3,
            "op": 4,
            "root": 5
        }

        level_names = {
            0: "Everyone",
            1: "Alumni",
            2: "Moderators",
            3: "Admins",
            4: "Operators",
            5: "Root"
        }

        user_level = ROLE_LEVELS[get_level()]
        sorted_help = {level: [] for level in range(6)}

        for cog in self.bot.cogs.values():
            help_info = getattr(cog, "__help__", None)
            if help_info:
                for cmd, meta in help_info.items():
                    args = meta.get("args", "")
                    desc = meta.get("desc", "")
                    perms = meta.get("perm", "everyone")

                    if isinstance(perms, str):
                        perms = [perms]

                    required_level = min(ROLE_LEVELS.get(p, 99) for p in perms)
                    if user_level >= required_level:
                        cmd_line = f"``!{cmd} {args}`` — {desc}" if args else f"``!{cmd}`` — {desc}"
                        sorted_help[required_level].append(cmd_line)

        embed = discord.Embed(
            title="Available Commands",
            color=discord.Color.blurple()
        )

        for level in sorted(sorted_help.keys()):
            if sorted_help[level]:
                embed.add_field(
                    name=level_names[level],
                    value="\n".join(sorted_help[level]),
                    inline=False
                )

        await ctx.send(embed=embed)


# This setup function adds the cog to the bot
def setup(bot):
    bot.add_cog(HelpCog(bot))
