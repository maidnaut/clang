import discord, os, asyncio, argparse
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *
import aiohttp

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):

    # Cogs
    bot.add_cog(WikiCog(bot))




#################################################################################




#################################################################################
# !template command
#################################################################################
class WikiCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Help info
        self.__help__ = {
            "aw": {
                "args": "",
                "desc": "Searches the wiki",
                "perm": "everyone"
            },
            "gw": {
                "args": "<query>",
                "desc": "Searches the Gentoo Wiki",
                "perm": "everyone"
            }
        }

    @commands.command()
    async def aw(self, ctx, *, query: str):
        await self._search_wiki(
            ctx = ctx,
            query = query,
            wiki_name = "Arch Wiki",
            base_url = "https://wiki.archlinux.org",
            search_url = "https://wiki.archlinux.org/api.php",
            thumbnail = "https://i.imgur.com/iH8a5Bd.png",
            fail_emoji = "<:bruh:1371231771462729730>",
            embed_color = discord.Color.blue()
        )

    @commands.command()
    async def gw(self, ctx, *, query: str):
        await self._search_wiki(
            ctx = ctx,
            query = query,
            wiki_name = "Gentoo Wiki",
            base_url = "https://wiki.gentoo.org",
            search_url = "https://wiki.gentoo.org/api.php",
            thumbnail = "https://i.imgur.com/hnQbCSU.png",
            fail_emoji = "<:bruh:1371231771462729730>",
            embed_color = discord.Color.from_rgb(230, 230, 230)
        )

    async def _search_wiki(self, ctx, query, wiki_name, base_url, search_url, thumbnail, fail_emoji, embed_color):
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params) as resp:
                if resp.status != 200:
                    await ctx.send(f"{ctx.author.mention} I couldn't contact {wiki_name}. {fail_emoji}")
                    return
                data = await resp.json()

        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            await ctx.send(f"{ctx.author.mention} No results found on the {wiki_name} for `{query}`. {fail_emoji}")
            return

        top_result = search_results[0]
        title = top_result["title"]
        page_url = f"{base_url}/wiki/{title.replace(' ', '_')}"

        if query == "clang":
            await ctx.send(f"Yes hello, that's me. Also here's the search result:")
        
        embed = discord.Embed(color=embed_color, title=f"{title}")
        embed.set_thumbnail(url=f"{thumbnail}")
        embed.add_field(name=f"",   value=f"{page_url}")
        await ctx.send(embed=embed)