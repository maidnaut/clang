import discord, os, asyncio, argparse, urllib.parse
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
            },
            "proton": {
                "args": "<query>",
                "desc": "Searches the ProtonDB",
                "perm": "everyone"
            }
        }

    wiki = discord.SlashCommandGroup("wiki", "Wiki related commands")




    # Wiki Search
    async def _search_wiki(self, ctx, query, wiki_name, base_url, search_url, thumbnail, fail_emoji, embed_color, slashcommand: bool = False):
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params) as resp:
                if resp.status != 200:
                    await ctx.send(f"{await author_ping(ctx)} I couldn't contact {wiki_name}. {fail_emoji}")
                    return
                data = await resp.json()

        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            await ctx.send(f"{await author_ping(ctx)} No results found on the {wiki_name} for `{query}`. {fail_emoji}")
            return

        top_result = search_results[0]
        title = top_result["title"]

        if wiki_name == "arch":
            page_url = f"{base_url}/title/{title.replace(' ', '_')}"
        else:
            url = f"{base_url}/wiki/{title.replace(' ', '_')}"
            parsed = urllib.parse.urlparse(url)
            segments = parsed.path.strip('/').split('/')
            
            if len(segments) > 2:
                new_path = '/' + '/'.join(segments[:-1])
                page_url = parsed._replace(path=new_path).geturl()
            else:
                page_url = url

        if query == "clang":
            await ctx.send(f"Yes hello, that's me. Also here's the search result:")
        
        embed = discord.Embed(color=embed_color, title=f"{title}")
        embed.set_thumbnail(url=f"{thumbnail}")
        embed.add_field(name=f"",   value=f"{page_url}")

        if slashcommand == True:
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            await ctx.send(embed=embed)

    # Proton Search
    async def _search_proton(self, ctx, title, slashcommand: bool = False):
        fail_emoji = "<:bruh:1371231771462729730>"

        steam_search_url = "https://store.steampowered.com/api/storesearch"
        params = {"term": title, "cc": "us", "l": "en"}

        async with aiohttp.ClientSession() as session:
            async with session.get(steam_search_url, params=params) as resp:
                if resp.status != 200:
                    await ctx.send(f"{await author_ping(ctx)} Couldn't search Steam. Status {resp.status} {fail_emoji}")
                    return
                data = await resp.json()

        if not data.get("items"):
            await ctx.send(f"{await author_ping(ctx)} No results found for `{title}` {fail_emoji}")
            return

        app = data["items"][0]
        app_id = app["id"]
        name = app["name"]
        protondb_url = f"https://www.protondb.com/app/{app_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(protondb_url) as resp:
                if resp.status == 200:
                    embed = discord.Embed(color=discord.Color.red(), title=f"{name}")
                    embed.set_thumbnail(url=f"https://i.imgur.com/i0xTLAb.png")
                    embed.add_field(name=f"",   value=f"{protondb_url}")

                    if slashcommand == True:
                        await ctx.respond(embed=embed, ephemeral=True)
                    else:
                        await ctx.send(embed=embed)
                else:
                    await ctx.send(f"{await author_ping(ctx)} No results found for `{name}` {fail_emoji}")




    # !aw
    @commands.command()
    async def aw(self, ctx, *, query: str = None):
        if query == None:
            await ctx.send(f"{await author_ping(ctx)} Please provide a search query. `!aw <query>`")

        await self._search_wiki(
            ctx = ctx,
            query = query,
            wiki_name = "arch",
            base_url = "https://wiki.archlinux.org",
            search_url = "https://wiki.archlinux.org/api.php",
            thumbnail = "https://i.imgur.com/iH8a5Bd.png",
            fail_emoji = "<:bruh:1371231771462729730>",
            embed_color = discord.Color.blue()
        )

    # !gw
    @commands.command()
    async def gw(self, ctx, *, query: str = None):
        if query == None:
            await ctx.send(f"{await author_ping(ctx)} Please provide a search query. `!gw <query>`")

        await self._search_wiki(
            ctx = ctx,
            query = query,
            wiki_name = "gentoo",
            base_url = "https://wiki.gentoo.org",
            search_url = "https://wiki.gentoo.org/api.php",
            thumbnail = "https://i.imgur.com/hnQbCSU.png",
            fail_emoji = "<:bruh:1371231771462729730>",
            embed_color = discord.Color.from_rgb(230, 230, 230)
        )

    # !proton
    @commands.command()
    async def proton(self, ctx, *, title: str = None):
        if title == None:
            await ctx.send(f"{await author_ping(ctx)} Please provide a search query. `!proton <query>`")

        await self._search_proton(ctx, title)




    # /wiki archwiki    
    @wiki.command(name="arch", description="Search the Arch Wiki")
    async def search_aw(self, ctx, query: str):
        await self._search_wiki(
            ctx = ctx,
            query = query,
            wiki_name = "Arch Wiki",
            base_url = "https://wiki.archlinux.org",
            search_url = "https://wiki.archlinux.org/api.php",
            thumbnail = "https://i.imgur.com/iH8a5Bd.png",
            fail_emoji = "<:bruh:1371231771462729730>",
            embed_color = discord.Color.blue(),
            slashcommand = True
        )

    # /wiki gentoowiki    
    @wiki.command(name="gentoo", description="Search the Gentoo Wiki")
    async def search_gw(self, ctx, query: str):
        await self._search_wiki(
            ctx = ctx,
            query = query,
            wiki_name = "Gentoo Wiki",
            base_url = "https://wiki.gentoo.org",
            search_url = "https://wiki.gentoo.org/api.php",
            thumbnail = "https://i.imgur.com/hnQbCSU.png",
            fail_emoji = "<:bruh:1371231771462729730>",
            embed_color = discord.Color.from_rgb(230, 230, 230),
            slashcommand = True
        )

    # /wiki proton   
    @wiki.command(name="proton", description="Search the Proton DB")
    async def search_proton(self, ctx, *, title: str):
        await self._search_proton(ctx, title, slashcommand = True)