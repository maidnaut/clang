import discord, os, random, asyncio, argparse, time, re
from inc.terminal import register_plugin
from discord.ext import commands
from inc.utils import *

#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):
    
    init_term()

    # Cogs
    bot.add_cog(CookieCog(bot))




#################################################################################




#################################################################################
# !cookies command suite
#################################################################################
class CookieCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.thank_cooldowns = {}
        self.THANK_COOLDOWN = 60
        self.THANK_LIMIT = 3

        # Help info
        self.__help__ = {
            "cookies": {
                "args": "",
                "desc": "Shows your cookies and supplies commands",
                "perm": "everyone"
            },
            "nom": {
                "args": "",
                "desc": "Eats a cookie",
                "perm": "everyone"
            },
            "give": {
                "args": "<user>",
                "desc": "Gives the mentioned user one of your cookies",
                "perm": "everyone"
            },
            "transfer": {
                "args": "<user> (amount)",
                "desc": "Cookie credit transfer",
                "perm": "everyone"
            },
            "airdrop": {
                "args": "<user> (amount)",
                "desc": "Hack in cookies",
                "perm": "admin"
            },
            "setrate": {
                "args": "(amount)",
                "desc": "Sets the rate for the random chance to recieve cookies on every message",
                "perm": "admin"
            },
        }

    # Make sure the cookies for the user exists and return an amouunt
    def check_cookies(self, guild_id, user_id):
        result = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
        
        if not result:
            try:
                db_insert("cookies", 
                        ["user_id", "guild_id", "cookies"],
                        [user_id, guild_id, 0])
                return 0
            except sqlite3.IntegrityError:
                result = db_read("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"])
                return result[0][3] if result else 0
        
        return result[0][3]

    async def membercheck(self, ctx, user_input: str) -> discord.Member:
        try:
            # Use pycord's converter to check for the member
            return await commands.MemberConverter().convert(ctx, user_input)
        except commands.MemberNotFound:
            try:
                # That didn't work, so check for numerics
                if user_input.isdigit():
                    return await ctx.guild.fetch_member(int(user_input))
            except discord.NotFound:
                pass
            await ctx.send(f"<@{ctx.author.id}> I couldn't find user '{user_input}' in this server.")
            return None
        except commands.BadArgument:
            await ctx.send(f"<@{ctx.author.id}> Invalid user format: {user_input}")
            return None

    # !coomies
    @commands.command()
    async def cookies(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id

        cookies = self.check_cookies(guild_id, user_id)

        await ctx.send(f"<@{ctx.author.id}> You have {cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")

    # !nom
    @commands.command()
    async def nom(self, ctx):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)

        cookies = self.check_cookies(guild_id, user_id)

        if cookies is None or cookies <= 0:
            await ctx.send("You don't have any cookies to eat!")
            return

        db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [("cookies", cookies - 1)])
        await ctx.send(f"<@{ctx.author.id}> You ate a cookie. You now have {cookies - 1} cookies.")

    # !give <user>
    @commands.command()
    async def give(self, ctx, user_input: str = None):
        if user_input is None:
            return await ctx.send(f"<@{ctx.author.id}> Please mention a user: `!give @user`")

        member = await self.membercheck(ctx, user_input)
        if not member:
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)
        guild_id = str(ctx.guild.id)

        if sender_id == receiver_id:
            return await ctx.send(f"<@{ctx.author.id}> You can't send a cookie to yourself!")

        sender_cookies = self.check_cookies(guild_id, sender_id)
        if sender_cookies < 1:
            return await ctx.send("You don't have any cookies to give!")

        receiver_cookies = self.check_cookies(guild_id, receiver_id)

        db_update("cookies",
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"],
                [("cookies", sender_cookies - 1)])
        
        db_update("cookies",
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"],
                [("cookies", receiver_cookies + 1)])
        
        await ctx.send(f"<@{ctx.author.id}> gave a cookie to {member.mention}!")

    # !transfer <user< <amount>
    @commands.command()
    async def transfer(self, ctx, user_input: str = None, amount: str = None):
        if user_input is None or amount is None:
            return await ctx.send(f"<@{ctx.author.id}> Usage: `!transfer @user amount`")

        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send(f"<@{ctx.author.id}> Please provide a valid amount.")
        
        if amount <= 0:
            return await ctx.send(f"<@{ctx.author.id}> Amount must be positive!")

        member = await self.membercheck(ctx, user_input)
        if not member:
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)
        guild_id = str(ctx.guild.id)

        sender_cookies = self.check_cookies(guild_id, sender_id)
        if sender_cookies < amount:
            return await ctx.send(f"<@{ctx.author.id}> You don't have enough cookies to transfer {amount}!")

        receiver_cookies = self.check_cookies(guild_id, receiver_id)

        db_update("cookies", 
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"], 
                [("cookies", sender_cookies - amount)])
        
        db_update("cookies", 
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"], 
                [("cookies", receiver_cookies + amount)])

        await ctx.send(f"<@{ctx.author.id}> Transferred {amount} cookies to {member.mention}!")

    # !setrate <int>
    @commands.command()
    async def setrate(self, ctx, rate: int = None):

        user_level = await get_level(ctx)

        if user_level < 4:
            return

        if user_level == 4:
            return await ctx.send("!op?")
        
        if rate is None:
            await ctx.send(f"<@{ctx.author.id}> ``!setrate <int>``")
            return
        
        if rate <= 0:
            await ctx.send(f"<@{ctx.author.id}> Rate must be positive!")
            return

        guild_id = ctx.guild.id
        db_update("cookie_rate", 
                [f"guild_id:{guild_id}"], 
                [("rate", rate)])

        await ctx.send(f"Cookie drop rate set to 1 in {rate} messages.")

    # !airdrop <user> <int>
    @commands.command()
    async def airdrop(self, ctx, user: discord.User = None, amount: int = None):
        
        user_level = await get_level(ctx)

        if user_level < 4:
            return

        if user_level == 4:
            return await ctx.send("!op?")
        
        if user is None or amount is None:
            await ctx.send(f"<@{ctx.author.id}> ``!airdrop <@user> <int>``")
            return
        
        if amount <= 0:
            await ctx.send(f"<@{ctx.author.id}> Amount must be positive!")
            return

        guild_id = ctx.guild.id
        user_id = str(user.id)

        cookies = self.check_cookies(guild_id, user_id)
        db_update("cookies", 
                [f"user_id:{user_id}", f"guild_id:{guild_id}"], 
                [("cookies", cookies + amount)])

        await ctx.send(f"Airdropped {amount} cookies to {user.name}! They now have {cookies + amount} cookies.")

    # Cookie drop & thanks
    @commands.Cog.listener()
    async def on_message(self, message):

        # Don't self check
        if message.author.bot:
            return

        # Drop out if we're in dm's
        if message.guild is None:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        
        # Random cookie drop
        rate = db_read("cookie_rate", [f"guild_id:{guild_id}"])
        rate = int(rate[0][2]) if rate else 100
        
        if random.randint(1, rate) == 1:
            current = self.check_cookies(guild_id, user_id)
            db_update("cookies",
                    [f"user_id:{user_id}", f"guild_id:{guild_id}"],
                    [("cookies", current + 1)])

        # Thanks
        thank_words = r"\b(thank(?:s| you)?|thx|ty(?:sm|vm)?|thnx)\b"
        contains_thank = bool(re.search(thank_words, message.content.lower()))
        
        if contains_thank:
            if guild_id not in self.thank_cooldowns:
                self.thank_cooldowns[guild_id] = {}
            
            user_cooldown = self.thank_cooldowns[guild_id].get(user_id, {"count": 0, "time": 0})
            
            current_time = int(time.time())
            if current_time - user_cooldown["time"] < self.THANK_COOLDOWN:
                if user_cooldown["count"] >= self.THANK_LIMIT:
                    await message.channel.send(
                        "Too many thank you's!!!",
                    )
                    return
                else:
                    user_cooldown["count"] += 1
            else:
                user_cooldown = {"count": 1, "time": current_time}
            
            self.thank_cooldowns[guild_id][user_id] = user_cooldown
            
            thanked_users = []
            thanked_users.extend([u for u in message.mentions if u.id != message.author.id])
            
            if message.reference:
                try:
                    replied_msg = await message.channel.fetch_message(message.reference.message_id)
                    if replied_msg.author.id != message.author.id:
                        thanked_users.append(replied_msg.author)
                except:
                    pass
            
            thanked_users = list({u.id: u for u in thanked_users}.values())
            
            if thanked_users:
                for user in thanked_users:
                    uid = str(user.id)
                    current = self.check_cookies(guild_id, uid)
                    db_update("cookies",
                            [f"user_id:{uid}", f"guild_id:{guild_id}"],
                            [("cookies", current + 1)])
                
                if len(thanked_users) == 1:
                    await message.channel.send(f"{thanked_users[0].mention} received a thank you cookie!")
                else:
                    names = ", ".join(u.mention for u in thanked_users[:-1]) + f" and {thanked_users[-1].mention}"
                    await message.channel.send(f"{names} received thank you cookies!")




#################################################################################




#################################################################################
# Register terminal stuff
#################################################################################
def init_term():

    # Init some text we'll use later
    usage = "command_name [-args] [guild_id:optional]"
    
    example = """
    Usage example goes here
    """

    def function(args: list[str]):

        # Put the terminal response function here
        print("todo")

    # Help page & register
    register_plugin(
        name="template",
        help=f"""
template: {usage}
    Put the description here

    Options:
        --args           Explanation of arg

    Extra information here

    Usage:
{example}


""",
        func=function
    )