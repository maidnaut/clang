import discord, os, asyncio, argparse, random, math
from inc.terminal import register_plugin
from discord.ext import commands
from datetime import datetime
from inc.utils import *

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):

    # Cogs
    bot.add_cog(NotesCog(bot))




#################################################################################




#################################################################################
# Notes cog
#################################################################################
class NotesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not table_exists("notes"):
            new_db("notes", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild", "INTEGER"),
                ("author", "INTEGER"),
                ("title", "TEXT"),
                ("content", "TEXT"),
                ("creation_date", "TEXT"),
            ])

    # Read the note
    async def _read(self, ctx, title, alias):
        notes = db_read("notes", [f"guild:{ctx.guild.id}", f"title:{title}"])

        if notes:
            note = random.choice(notes)

            note_id = note[0]
            note_author = note[2]
            note_title = note[3]
            note_content = note[4]

            dt = datetime.fromisoformat(note[5])
            note_date = dt.strftime("%B %d, %Y")

            # Find the author
            author = await self.bot.fetch_user(int(note_author))

            if alias:
                msg = f"``#{note_id} - {note_title}:`` 📣 {note_content}"
                await ctx.send(msg)
            else:
                msg = f"{author.mention} ``- {note_date}``\n"
                msg += f"``#{note_id} - {note_title}:`` \n\n📣 {note_content}"
                await ctx.send(msg)
        else:
            await ctx.send(f"No note found with title `{title}`.")

    # Read the note
    async def _read_id(self, ctx, id):
        note = db_read("notes", [f"id:{id}", f"guild:{ctx.guild.id}"])

        if note:

            note_id = note[0][0]
            note_author = note[0][2]
            note_title = note[0][3]
            note_content = note[0][4]

            dt = datetime.fromisoformat(note[0][5])
            note_date = dt.strftime("%B %d, %Y")

            # Find the author
            author = await self.bot.fetch_user(int(note_author))

            msg = f"{author.mention} ``- {note_date}``\n"
            msg += f"``#{note_id} - {note_title}:`` \n\n📣 {note_content}"
            await ctx.send(msg)
        else:
            await ctx.send(f"No note found with id `{id}`.")

    # New
    async def _new(self, ctx, title, content):
        db_insert("notes",
                  ["guild", "author", "title", "content", "creation_date"],
                  [ctx.guild.id, ctx.author.id, title, content, discord.utils.utcnow().isoformat()])
        await ctx.send(f"Note `{title}` saved.")

    # Aliases
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)

        if message.content.startswith("... "):
            title = message.content[4:].strip()
            await self._read(ctx, title, alias=True)

        elif message.content.startswith(".. "):
            args = message.content[3:].strip().split(maxsplit=1)
            if len(args) < 2:
                await message.channel.send("Usage: `.. <title> <content>`")
                return
            title, content = args
            await self._new(ctx, title, content)


    # Read note
    @commands.command()
    async def n(self, ctx, *, title: str = None):
        if not title:
            await ctx.send("Usage: `!n <title>`")
            return

        await self._read(ctx, title, alias=False)


    # Read note by id
    @commands.command()
    async def nid(self, ctx, *, id: str = None):
        if not id:
            await ctx.send(f"{ctx.author} Please provide an ID: `!nid <id>`")
            return

        if not id.isdigit():
            await ctx.send(f"{ctx.author} Please provide an ID: `!nid <id>`")
            return

        await self._read_id(ctx, id)




    # New note
    @commands.command()
    async def new(self, ctx, title: str = None, *, content: str = None):
        if not title or not content:
            await ctx.send("Usage: `!new <title> <content>`")
            return
        await self._new(ctx, title, content)





    # Delete Note
    @commands.command()
    async def dn(self, ctx, *, id: int = None):
        if not id:
            await ctx.send("Usage: `!dn <id>`")
            return

        note = db_read("notes", [f"guild:{ctx.guild.id}", f"id:{id}"])
        if not note:
            await ctx.send(f"No note found with ID `{id}`.")
            return

        note = note[0]
        title = note[3]
        author = int(note[2])  # ensure it's int for comparison

        user_level = await get_level(ctx)

        # Only allow if author or elevated
        if ctx.author.id != author and user_level < 1:
            await ctx.send(f"{ctx.author.mention} You can only delete your own notes.")
            return

        db_remove("notes", ["guild", "id"], [ctx.guild.id, id])
        await ctx.send(f"Note `{title}` deleted.")



    # List notes
    @commands.command()
    async def ln(self, ctx):
        await ctx.message.delete()

        notes = db_read("notes", [f"guild:{ctx.guild.id}"])
        if not notes:
            await ctx.send("No notes saved.", delete_after=10)
            return

        per_page = 15
        pages = math.ceil(len(notes) / per_page)
        current = 0

        def make_embed(page):
            start = page * per_page
            end = start + per_page
            titles = [f"◆   ``#{note[0]} - {note[3]}``" for note in notes[start:end]]
            embed = discord.Embed(
                title=f"Notes (Page {page+1}/{pages})",
                description="\n".join(titles),
                color=0x00cc99
            )
            return embed

        message = await ctx.send(embed=make_embed(current))

        if pages == 1:
            await asyncio.sleep(120)
            await message.delete()
            return

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["⬅️", "➡️"]
                and reaction.message.id == message.id
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=120.0, check=check)
                if str(reaction.emoji) == "➡️" and current < pages - 1:
                    current += 1
                    await message.edit(embed=make_embed(current))
                elif str(reaction.emoji) == "⬅️" and current > 0:
                    current -= 1
                    await message.edit(embed=make_embed(current))
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.delete()
                break
