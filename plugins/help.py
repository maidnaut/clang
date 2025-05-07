import discord
from discord.ext import commands
from inc.utils import db_read, get_level

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx):
        user_level = await get_level(ctx)
        print(user_level)

        # Setup bucketized responses, so we (hopefully) don't go over the character limit
        buckets = {i: [] for i in range(6)}
        for cog in self.bot.cogs.values():
            help_info = getattr(cog, "__help__", None)
            if not help_info:
                continue

            # Gather all the help data
            for cmd, meta in help_info.items():
                args = meta.get("args", "")
                desc = meta.get("desc", "")
                raw  = meta.get("perm", "everyone")
                perms = [raw] if isinstance(raw, str) else raw
                perm  = perms[0].strip().lower()

                # Get the required perm level
                if   perm == "everyone": req = 0
                elif perm == "submod":   req = 1
                elif perm == "mod":      req = 2
                elif perm == "op":       req = 3
                elif perm == "admin":    req = 4
                elif perm == "root":     req = 5
                else:                    req = 0

                # If we meet the level requirements, add it to the list
                if user_level >= req:
                    line = f"``!{cmd} {args}`` — {desc}" if args else f"``!{cmd}`` — {desc}"
                    buckets[req].append(line)

        everyone_cmds = buckets[0]
        your_cmds = []
        for lvl in range(1, 6):
            your_cmds.extend(buckets[lvl])

        # Do some magic to build the buckets
        def chunk_lines(lines):
            pages = []
            current = []
            length = 0
            for line in lines:
                if length + len(line) + 1 > 1024:
                    pages.append("\n".join(current))
                    current = [line]
                    length = len(line) + 1
                else:
                    current.append(line)
                    length += len(line) + 1
            if current:
                pages.append("\n".join(current))
            return pages

        # @everyone commands list
        for page in chunk_lines(everyone_cmds):
            e = discord.Embed(title="@Everyone Commands", color=discord.Color.blurple())
            e.description = page
            await ctx.send(embed=e)

        # your elevated commands list
        if your_cmds:
            for page in chunk_lines(your_cmds):
                e = discord.Embed(title="Your Commands", color=discord.Color.blurple())
                e.description = page
                await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(HelpCog(bot))
