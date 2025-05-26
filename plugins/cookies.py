import discord, os, random, asyncio, argparse, time, re
from discord.ext import commands
from inc.utils import *

# fmt: off
#################################################################################
# Handle shell commands and help page
#################################################################################

def setup(bot):

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
            "leaderboard": {
                "args": "",
                "desc": "Shows the cookie leaderboard",
                "perm": "everyone"
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
            await ctx.send(f"{await author_ping(ctx)} I couldn't find user '{user_input}' in this server.")
            return None
        except commands.BadArgument:
            await ctx.send(f"{await author_ping(ctx)} Invalid user format: {user_input}")
            return None

    # !coomies
    @commands.command()
    async def cookies(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id

        cookies = self.check_cookies(guild_id, user_id)

        await ctx.send(f"{await author_ping(ctx)} You have {cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")

    # !nom
    @commands.command()
    async def nom(self, ctx):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)

        cookies = self.check_cookies(guild_id, user_id)

        if cookies is None or cookies <= 0:
            await ctx.send(f"{await author_ping(ctx)} You don't have any cookies to eat!")
            return

        db_update("cookies", [f"user_id:{user_id}", f"guild_id:{guild_id}"], [("cookies", cookies - 1)])
        await ctx.send(f"{await author_ping(ctx)} You ate a cookie. You now have {cookies - 1} cookies.")

    # !give <user>
    @commands.command()
    async def give(self, ctx, user_input: str = None):
        if user_input is None:
            return await ctx.send(f"{await author_ping(ctx)} Please mention a user: `!give @user`")

        member = await self.membercheck(ctx, user_input)
        if not member:
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)
        guild_id = str(ctx.guild.id)

        if sender_id == receiver_id:
            return await ctx.send(f"{await author_ping(ctx)} You can't send a cookie to yourself!")

        sender_cookies = self.check_cookies(guild_id, sender_id)
        if sender_cookies < 1:
            return await ctx.send(f"{await author_ping(ctx)} You don't have any cookies to give!")

        receiver_cookies = self.check_cookies(guild_id, receiver_id)

        db_update("cookies",
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"],
                [("cookies", sender_cookies - 1)])
        
        db_update("cookies",
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"],
                [("cookies", receiver_cookies + 1)])
        
        await ctx.send(f"{author_ping(ctx)} gave a cookie to {user_ping(ctx)}!")

    # !transfer <user< <amount>
    @commands.command()
    async def transfer(self, ctx, user_input: str = None, amount: str = None):
        if user_input is None or amount is None:
            return await ctx.send(f"{await author_ping(ctx)} Usage: `!transfer @user amount`")

        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send(f"{await author_ping(ctx)} Please provide a valid amount.")
        
        if amount <= 0:
            return await ctx.send(f"{await author_ping(ctx)} Amount must be positive!")

        member = await self.membercheck(ctx, user_input)
        if not member:
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)
        guild_id = str(ctx.guild.id)

        sender_cookies = self.check_cookies(guild_id, sender_id)
        if sender_cookies < amount:
            return await ctx.send(f"{await author_ping(ctx)} You don't have enough cookies to transfer {amount}!")

        receiver_cookies = self.check_cookies(guild_id, receiver_id)

        db_update("cookies", 
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"], 
                [("cookies", sender_cookies - amount)])
        
        db_update("cookies", 
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"], 
                [("cookies", receiver_cookies + amount)])

        await ctx.send(f"{await author_ping(ctx)}Transferred {amount} cookies to {await user_ping(ctx)}!")

    # !setrate <int>
    @commands.command()
    async def setrate(self, ctx, rate: int = None):

        user_level = await get_level(ctx)

        if user_level < 4:
            return

        if user_level == 4:
            return await ctx.send("!op?")
        
        if rate is None:
            await ctx.send(f"{await author_ping(ctx)} ``!setrate <int>``")
            return
        
        if rate <= 0:
            await ctx.send(f"{await author_ping(ctx)} Rate must be positive!")
            return

        guild_id = ctx.guild.id
        db_update("cookie_rate", 
                [f"guild_id:{guild_id}"], 
                [("rate", rate)])

        await ctx.send(f"{await author_ping(ctx)} Cookie drop rate set to 1 in {rate} messages.")

    # !airdrop <user> <int>
    @commands.command()
    async def airdrop(self, ctx, user: discord.User = None, amount: int = None):
        
        user_level = await get_level(ctx)

        if user_level < 4:
            return

        if user_level == 4:
            return await ctx.send("!op?")
        
        if user is None or amount is None:
            await ctx.send(f"{await author_ping(ctx)} ``!airdrop <@user> <int>``")
            return
        
        if amount <= 0:
            await ctx.send(f"{await author_ping(ctx)} Amount must be positive!")
            return

        guild_id = ctx.guild.id
        user_id = str(user.id)

        cookies = self.check_cookies(guild_id, user_id)
        db_update("cookies", 
                [f"user_id:{user_id}", f"guild_id:{guild_id}"], 
                [("cookies", cookies + amount)])

        await ctx.send(f"{await author_ping(ctx)} Airdropped {amount} cookies to {await user_ping(ctx)}! They now have {cookies + amount} cookies.")

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
        preNoPattern1 = r"\b(?<!no)"
        preNoPattern2 = r"\b(?<!no\s)"
        postNoPattern = r"(?! but)"
        middleThanksPattern = r"\b(thank(?:s|you)?|thx|ty(?:sm|vm)?|thnx|danke|gracias|merci|xeixei|dhonnobad|grazie|obrigado|spasibo|arigato|arigatou?|gomawo|gamsahamnida|shukran|shukriya|kiitos|asante|efcharisto)\b"

        if re.search(
                f"{preNoPattern1}{middleThanksPattern}{postNoPattern}", message.content, flags=re.IGNORECASE
            ) and re.search(
                f"{preNoPattern2}{middleThanksPattern}{postNoPattern}", message.content, flags=re.IGNORECASE
            ):
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
                    await message.channel.send(f"{await check_ping(thanked_users[0])} received a thank you cookie!")
                else:
                    names = ", ".join(u.mention for u in thanked_users[:-1]) + f" and {await check_ping(thanked_users[-1])}"
                    await message.channel.send(f"{names} received thank you cookies!")

    @commands.command()
    async def leaderboard(self, ctx):
        guild_id = ctx.guild.id
        cookies = db_read("cookies", [f"guild_id:{guild_id}"])
        
        cookies = sorted(cookies, key=lambda x: x[3], reverse=True)
        top_10 = cookies[:10]

        leaderboard = ""
        for i, cookie in enumerate(top_10, start=1):
            user = await get_user(ctx, cookie[2])
            if user != "N/A":
                leaderboard += f"**#{i}** {await user_ping(ctx)} - {cookie[3]}\n"

        await ctx.send(embed=discord.Embed(
            title="Cookie Leaderboard",
            description=leaderboard or "No cookie data found.",
            color=discord.Color.gold()
        ))