import discord
from discord.ext import commands
from inc.utils import db_read, get_level

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_help_data(self, ctx):

        user_level = await get_level(ctx)
        buckets = {i: [] for i in range(6)}

        for cog in self.bot.cogs.values():
            help_info = getattr(cog, "__help__", None)
            if not help_info:
                continue

            for cmd, meta in help_info.items():
                args = meta.get("args", "")
                desc = meta.get("desc", "")
                raw = meta.get("perm", "everyone")
                perms = [raw] if isinstance(raw, str) else raw
                perm = perms[0].strip().lower()

                perm_levels = {
                    "everyone": 0,
                    "submod": 1,
                    "mod": 2,
                    "op": 3,
                    "admin": 4,
                    "root": 5
                }
                req = perm_levels.get(perm, 0)

                if user_level >= req:
                    line = f"``!{cmd} {args}`` — {desc}" if args else f"``!{cmd}`` — {desc}"
                    buckets[req].append(line)

        return buckets

    def chunk_lines(self, lines):

        pages = []
        current = []
        length = 0
        for line in lines:
            if length + len(line) + 1 > 2000:
                pages.append("\n".join(current))
                current = [line]
                length = len(line) + 1
            else:
                current.append(line)
                length += len(line) + 1
        if current:
            pages.append("\n".join(current))
        return pages

    @commands.command()
    async def cheatsheet(self, ctx):

        buckets = await self.get_help_data(ctx)

        your_cmds = []
        for lvl in range(1, 6):
            your_cmds.extend(buckets[lvl])

        if your_cmds:
            e = "**Cheatsheet**\n"
            for page in self.chunk_lines(your_cmds):
                e += page
                await ctx.send(e)

    @commands.command()
    async def help(self, ctx):
        
        buckets = await self.get_help_data(ctx)
        everyone_cmds = buckets[0]

        e = "**Commands**\n"
        for page in self.chunk_lines(everyone_cmds):
            e += page
            await ctx.send(e)

def setup(bot):
    bot.add_cog(HelpCog(bot))
