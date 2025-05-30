import discord, os, random, asyncio, argparse, time, re, math
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
        self.gamble_cooldowns = {}
        self.gamble_blocks = {}
        self.THANK_COOLDOWN = 60
        self.THANK_LIMIT = 3
        self.GAMBLE_LIMIT = 10
        self.GAMBLE_WINDOW = 30
        self.MAX_COOKIES = 1000000

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
            "take": {
                "args": "<user> (amount)",
                "desc": "Delete cookies",
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
            "gamble": {
                "args": "<amount/all>",
                "desc": "(Alias: !bet) Gamble your cookies for a chance to win more",
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

    # !cookies
    @commands.command()
    async def cookies(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id

        cookies = self.check_cookies(guild_id, user_id)
        formatted_cookies = f"{cookies:,}"

        await ctx.send(f"{await author_ping(ctx)} You have {formatted_cookies} cookies.\n-# Use ``!give <@user>``, or reply with the word thanks to give. Use ``!nom`` to eat one.")

    # !nom
    @commands.command()
    async def nom(self, ctx):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)

        cookies = self.check_cookies(guild_id, user_id)

        if cookies is None or cookies <= 0:
            await ctx.send(f"{await author_ping(ctx)} You don't have any cookies to eat!")
            return

        new_balance = cookies - 1
        formatted_new = f"{new_balance:,}"
        formatted_old = f"{cookies:,}"

        db_update("cookies", 
                 [f"user_id:{user_id}", f"guild_id:{guild_id}"], 
                 [("cookies", new_balance)])
        
        await ctx.send(
            f"{await author_ping(ctx)} You ate a cookie. "
            f"You now have {formatted_new} cookies."
        )

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

        # Check if receiver is at cookie cap
        if receiver_cookies >= self.MAX_COOKIES:
            return await ctx.send(f"{await author_ping(ctx)} I can't give a cookie to {await user_ping(ctx, member)}, they've already won capitalism!")

        # Calculate remaineder from max
        available_space = self.MAX_COOKIES - receiver_cookies
        actual_give = min(1, available_space)

        db_update("cookies",
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"],
                [("cookies", sender_cookies - 1)])
        
        db_update("cookies",
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"],
                [("cookies", receiver_cookies + actual_give)])

        # Handle 1,000,000 case
        if receiver_cookies + actual_give == self.MAX_COOKIES:
            await ctx.send(
                f"{await author_ping(ctx)} gave a cookie to {await user_ping(ctx, member)}!\n"
                f"💎💎💎 **{await user_ping(ctx, member)} YOU WON CAPITALISM!** 💎💎💎"
            )
        else:
            await ctx.send(f"{await author_ping(ctx)} gave a cookie to {await user_ping(ctx, member)}!")
        

    # !transfer <user< <amount>
    @commands.command()
    async def transfer(self, ctx, user_input: str = None, amount: str = None):

        if user_input is None or amount is None:
            return await ctx.send(f"{await author_ping(ctx)} Usage: `!transfer @user amount`")

        try:
            amount_int = int(amount)
        except ValueError:
            return await ctx.send(f"{await author_ping(ctx)} Please provide a valid amount.")
        
        if amount_int <= 0:
            return await ctx.send(f"{await author_ping(ctx)} Amount must be positive!")

        member = await self.membercheck(ctx, user_input)
        if not member:
            return

        if member == ctx.author:
            return await ctx.send(f"{await author_ping(ctx)} You can't transfer cookies to yourself!")
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)
        guild_id = str(ctx.guild.id)

        sender_cookies = self.check_cookies(guild_id, sender_id)
        if sender_cookies < amount_int:
            return await ctx.send(f"{await author_ping(ctx)} You don't have enough cookies to transfer {amount_int}!")

        receiver_cookies = self.check_cookies(guild_id, receiver_id)

        # Check if they won capitalism
        if receiver_cookies >= self.MAX_COOKIES:
            return await ctx.send(f"{await author_ping(ctx)} I can't transfer cookies to {await user_ping(ctx, member)}, they've already won capitalism!")

        # Calc remainder from limit
        available_space = self.MAX_COOKIES - receiver_cookies
        actual_transfer = min(amount_int, available_space)
        
        # Actual cookie transfer
        receiver_new_balance = receiver_cookies + actual_transfer
        
        # Update balances
        db_update("cookies",
                [f"user_id:{sender_id}", f"guild_id:{guild_id}"],
                [("cookies", sender_cookies - actual_transfer)])
        
        db_update("cookies",
                [f"user_id:{receiver_id}", f"guild_id:{guild_id}"],
                [("cookies", receiver_new_balance)])

        # Did they win?
        if actual_transfer < amount_int:
            # Partial transfer
            response = (
                f"{await author_ping(ctx)} transferred {actual_transfer:,} of {amount_int:,} cookies to "
                f"{await user_ping(ctx, member)} (reached capitalism cap)"
            )
        else:
            # Full transfer
            response = f"{await author_ping(ctx)} transferred {actual_transfer:,} cookies to {await user_ping(ctx, member)}!"

        # They won!
        if receiver_new_balance == self.MAX_COOKIES:
            response += f"\💎💎💎 **{await user_ping(ctx, member)} YOU WON CAPITALISM!** 💎💎💎"

        await ctx.send(response)

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

        # Permission check
        user_level = await get_level(ctx)
        if user_level < 4:
            return
        if user_level == 4:
            return await ctx.send("!op?")
        
        # Input validation
        if user is None or amount is None:
            return await ctx.send(f"{await author_ping(ctx)} ``!airdrop <@user> <int>``")
        if amount <= 0:
            return await ctx.send(f"{await author_ping(ctx)} Amount must be positive!")

        guild_id = ctx.guild.id
        user_id = str(user.id)
        current = self.check_cookies(guild_id, user_id)

        # Calc remainder from cap
        available_space = max(0, self.MAX_COOKIES - current)
        actual_airdrop = min(amount, available_space)
        new_balance = current + actual_airdrop

        # Update database
        db_update("cookies", 
                 [f"user_id:{user_id}", f"guild_id:{guild_id}"], 
                 [("cookies", new_balance)])

        # Response
        if actual_airdrop == 0:
            response = f"{await user_ping(ctx, user)} already has {current:,} cookies - no airdrop needed!"
        elif actual_airdrop < amount:
            response = (
                f"Airdropped {actual_airdrop:,} of {amount:,} cookies to {await user_ping(ctx, user)} "
                f"(reached capitalism cap). New balance: {new_balance:,}"
            )
        else:
            response = (
                f"Airdropped {actual_airdrop:,} cookies to {await user_ping(ctx, user)}! "
                f"New balance: {new_balance:,}"
            )
            
        # Did they win?
        if new_balance == self.MAX_COOKIES:
            response += f"\n💎💎💎 **{await user_ping(ctx, user)} HAS WON CAPITALISM!** 💎💎💎"
        
        await ctx.send(f"{await author_ping(ctx)} {response}")



    # !take <user> <int>
    @commands.command()
    async def take(self, ctx, user: discord.User = None, amount: int = None):
        
        user_level = await get_level(ctx)

        if user_level < 4:
            return

        if user_level == 4:
            return await ctx.send("!op?")
        
        if user is None or amount is None:
            await ctx.send(f"{await author_ping(ctx)} ``!take <@user> <int>``")
            return
        
        if amount <= 0:
            await ctx.send(f"{await author_ping(ctx)} Amount must be positive!")
            return

        guild_id = ctx.guild.id
        user_id = str(user.id)

        cookies = self.check_cookies(guild_id, user_id)
        db_update("cookies", 
                [f"user_id:{user_id}", f"guild_id:{guild_id}"], 
                [("cookies", cookies - amount)])

        await ctx.send(f"{await author_ping(ctx)} Took {amount} cookies from {await user_ping(ctx, user)}! They now have {cookies - amount} cookies.")

    # !setcookies <user> <int>
    @commands.command()
    async def setcookies(self, ctx, user: discord.User = None, amount: int = None):
        # Permission check
        user_level = await get_level(ctx)
        if user_level < 4:
            return
        if user_level == 4:
            return await ctx.send("!op?")
        
        # Input validation
        if user is None or amount is None:
            return await ctx.send(f"{await author_ping(ctx)} ``!setcookies <@user> <int>``")
        if amount <= 0:
            return await ctx.send(f"{await author_ping(ctx)} Amount must be positive!")

        guild_id = ctx.guild.id
        user_id = str(user.id)
        
        # Cap
        capped_amount = min(amount, self.MAX_COOKIES)
        
        # Update database
        db_update("cookies", 
                [f"user_id:{user_id}", f"guild_id:{guild_id}"], 
                [("cookies", capped_amount)])

        # Response
        if amount > self.MAX_COOKIES:
            response = (
                f"Set {await user_ping(ctx, user)}'s cookies to {capped_amount:,} "
                f"(capped from {amount:,} due to capitalism limit)"
            )
        else:
            response = f"Set {await user_ping(ctx, user)}'s cookies to {capped_amount:,}"

        # Did they win?
        if capped_amount == self.MAX_COOKIES:
            response += f"\n💎💎💎 **{await user_ping(ctx, user)} HAS WON CAPITALISM!** 💎💎💎"
        
        await ctx.send(f"{await author_ping(ctx)} {response}")

    # !resetcookies
    @commands.command()
    async def resetcookies(self, ctx):
        # Permission check
        user_level = await get_level(ctx)
        if user_level < 4:
            return
        if user_level == 4:
            return await ctx.send("!op?")

        guild_id = ctx.guild.id
        
        db_update("cookies", 
                [f"guild_id:{guild_id}"], 
                [("cookies", 0)])
        
        await ctx.send(f"{await author_ping(ctx)} All cookies in this server have been reset to 0!")

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
            if current < self.MAX_COOKIES:
                new_balance = min(current + 1, self.MAX_COOKIES)
                db_update("cookies",
                         [f"user_id:{user_id}", f"guild_id:{guild_id}"],
                         [("cookies", new_balance)])

        # Thanks handling with capitalism cap
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
                    await message.channel.send("Too many thank you's!!!")
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
                capitalism_achievers = []
                valid_recipients = []
                
                for user in thanked_users:
                    uid = str(user.id)
                    current_cookies = self.check_cookies(guild_id, uid)
                    
                    # Skip if user has already won capitalism
                    if current_cookies >= self.MAX_COOKIES:
                        continue
                    
                    # Calculate new balance with cap
                    new_balance = min(current_cookies + 1, self.MAX_COOKIES)
                    db_update("cookies",
                             [f"user_id:{uid}", f"guild_id:{guild_id}"],
                             [("cookies", new_balance)])
                    
                    valid_recipients.append(user)
                    
                    # Check if this thank made them reach exactly 1M
                    if new_balance == self.MAX_COOKIES:
                        capitalism_achievers.append(user)
                
                # Only send messages if there are valid recipients
                if valid_recipients:
                    ctx = await self.bot.get_context(message)
                    
                    if len(valid_recipients) == 1:
                        await message.channel.send(f"{await check_ping(ctx, valid_recipients[0])} received a thank you cookie!")
                    else:
                        names = ", ".join(u.mention for u in valid_recipients[:-1]) + f" and {await check_ping(ctx, valid_recipients[-1])}"
                        await message.channel.send(f"{names} received thank you cookies!")
                
                # Celebrate capitalism achievers
                for achiever in capitalism_achievers:
                    await message.channel.send(f"💎💎💎 {await check_ping(ctx, achiever)} HAS WON CAPITALISM! 💎💎💎")

    # !leaderboard
    @commands.command()
    async def leaderboard(self, ctx):
        guild_id = ctx.guild.id
        cookies = db_read("cookies", [f"guild_id:{guild_id}"])
        
        # Filter out users who have reached capitalism (1M+ cookies)
        active_players = [c for c in cookies if c[3] < self.MAX_COOKIES]
        active_players = sorted(active_players, key=lambda x: x[3], reverse=True)
        top_10 = active_players[:10]

        leaderboard = ""
        for i, cookie in enumerate(top_10, start=1):
            user = await get_user(ctx, cookie[2])
            if user != "N/A":
                formatted_cookies = f"{cookie[3]:,}"
                leaderboard += f"**#{i}** {await user_ping(ctx, user)} - {formatted_cookies}\n"

        embed = discord.Embed(
            title="Leaderboard",
            description=leaderboard or "Could not generate leaderboard.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    # !halloffame
    @commands.command()
    async def halloffame(self, ctx, page: int = 1):
        guild_id = ctx.guild.id
        cookies = db_read("cookies", [f"guild_id:{guild_id}"])
        
        # Get all capitalism achievers (1M+ cookies)
        hall_of_famers = [c for c in cookies if c[3] >= self.MAX_COOKIES]
        hall_of_famers = sorted(hall_of_famers, key=lambda x: x[3], reverse=True)
        
        if not hall_of_famers:
            await ctx.send("No one has won capitalism yet!")
            return
        
        # Pagination setup
        PER_PAGE = 10
        total_pages = (len(hall_of_famers) + PER_PAGE - 1) // PER_PAGE
        page = max(1, min(page, total_pages))
        
        start_index = (page - 1) * PER_PAGE
        end_index = start_index + PER_PAGE
        page_entries = hall_of_famers[start_index:end_index]
        
        hall_of_fame = ""
        for i, cookie in enumerate(page_entries, start=start_index+1):
            user = await get_user(ctx, cookie[2])
            if user != "N/A":
                formatted_cookies = f"{cookie[3]:,}"
                hall_of_fame += f"**💎 #{i}** {await user_ping(ctx, user)} - {formatted_cookies}\n"

        embed = discord.Embed(
            title="🏆 Filthy Capitalist Millionaires 🏆",
            description=hall_of_fame,
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text=f"Page {page}/{total_pages} | {len(hall_of_famers)} total capitalists")
        await ctx.send(embed=embed)

    # !gamba
    @commands.command(aliases=['bet'])
    async def gamble(self, ctx, amount: str = None):

        max_bet = 100
        
        user_id = ctx.author.id
        current_time = time.time()
        
        # Cooldown spam prevention
        if user_id in self.gamble_blocks:
            if current_time < self.gamble_blocks[user_id]:
                return
            del self.gamble_blocks[user_id]
        
        if user_id not in self.gamble_cooldowns:
            self.gamble_cooldowns[user_id] = []
        
        self.gamble_cooldowns[user_id] = [
            t for t in self.gamble_cooldowns[user_id] 
            if current_time - t < self.GAMBLE_WINDOW
        ]
        
        if len(self.gamble_cooldowns[user_id]) >= self.GAMBLE_LIMIT:
            # Calculate when the block should expire
            oldest = self.gamble_cooldowns[user_id][0]
            block_until = oldest + self.GAMBLE_WINDOW
            
            self.gamble_blocks[user_id] = block_until
            
            wait_time = int(block_until - current_time)
            await ctx.send(
                f"{await author_ping(ctx)} You've been rate limited! "
                f"Please wait {wait_time} seconds before gambling again."
            )
            
            del self.gamble_cooldowns[user_id]
            return
        
        self.gamble_cooldowns[user_id].append(current_time)
        
        if amount is None:
            await ctx.send(f"""
{await author_ping(ctx)} <:spamton:1377920510666739712> NOW'S YOUR CHANCE TO BE A [[BIGSHOT]]\n
How to gamba: Use ``!gamble`` or ``!bet`` with an amount under 100 to roll the dice to see how much you can win!\n
Betting ``half`` breaks the betting limit, but the higher you bet, the more dangerous the odds. Going all in with ``!bet all`` is even more risky than a half bet.\n
Remember, if you wanna win big, always bet on CLANG <:clang:1373291982528577566>
""")
            return

        guild_id = ctx.guild.id
        current = self.check_cookies(guild_id, str(user_id))

        if amount.lower() == "all":
            if current <= 0:
                await ctx.send(f"Sorry {await author_ping(ctx)}, you don't have any cookies. Come back when you're a little mmm, richer.")
                return
            amount_int = current
        elif amount.lower() == "half":
            if current <= 0:
                await ctx.send(f"Sorry {await author_ping(ctx)}, you don't have any cookies. Come back when you're a little mmm, richer.")
                return
            amount_int = int(current / 2)
        else:
            try:
                amount_int = int(amount)
            except ValueError:
                await ctx.send(f"{await author_ping(ctx)} Please enter a valid number or 'all/half'")
                return

        if amount_int <= 0:
            await ctx.send(f"{await author_ping(ctx)} Amount must be positive!")
            return

        if current < amount_int:
            await ctx.send(f"Sorry {await author_ping(ctx)}, I don't hand out cookies for free. Come back when you're a little mmm, richer.")
            return

        if amount.lower() != "all" and amount.lower() != "half":
            if amount_int > max_bet:
                await ctx.send(f"{await author_ping(ctx)} You can only spend {max_bet} cookies at a time!")
                return

        # Logarithmic scaling
        if current <= 5000:
            boost_factor = (5000 - current) / 5000
            boost = int(20 + 30 * boost_factor)
            base_roll = random.randint(0, 300)
            adjusted_roll = min(300, base_roll + boost)
        else:
            wealth_factor = min(1.0, math.log10(current) / math.log10(self.MAX_COOKIES))
            penalty = int(wealth_factor * 15)
            base_roll = random.randint(0, 300)
            adjusted_roll = max(0, base_roll - penalty)
            
        # Outcomes
        def get_outcome(roll_val, bet_type):
            if bet_type == "all":
                thresholds = [
                    # Roll / Multiplier
                    (285, 2.5),
                    (270, 1.8),
                    (240, 1.6),
                    (210, 1.4),
                    (180, 1.2),
                    (150, 1.0),
                    (120, 0.8),
                    (90, 0.6),
                    (60, 0.4),
                    (30, 0.2),
                    (15, 0.1),
                    (0, 0.0)
                ]
            else:
                thresholds = [
                    (280, 2.0),
                    (260, 1.5),
                    (245, 1.4),
                    (230, 1.3),
                    (200, 1.2),
                    (150, 1.0),
                    (100, 0.9),
                    (80, 0.8),
                    (60, 0.7),
                    (40, 0.6),
                    (20, 0.5),
                    (0, 0.0)
                ]

            # Regular thresholds
            for threshold, mult in thresholds:
                if roll_val >= threshold:
                    base_multiplier = mult
                    break
            else:
                base_multiplier = 0.0

            # Ultra rare gambas
            ultra_rare_hit = False
            if roll_val >= 280:
                ultra_rare = random.randint(1, 60)
                if ultra_rare >= 50:
                    final_multiplier = 4.0
                    ultra_rare_hit = True
                elif ultra_rare >= 40:
                    final_multiplier = 3.8
                    ultra_rare_hit = True
                elif ultra_rare >= 30:
                    final_multiplier = 3.6
                    ultra_rare_hit = True
                elif ultra_rare >= 20:
                    final_multiplier = 3.2
                    ultra_rare_hit = True
                elif ultra_rare >= 10:
                    final_multiplier = 3.0
                    ultra_rare_hit = True
                elif ultra_rare >= 0:
                    if bet_type == "all":
                        final_multiplier = 2.5
                    else:
                        final_multiplier = 2.0
                    
                    ultra_rare_hit = False
                else:
                    final_multiplier = base_multiplier
            else:
                final_multiplier = base_multiplier

            return final_multiplier, ultra_rare_hit

        # Determine outcome
        bet_type = "all" if amount.lower() == "all" else "fixed"
        multiplier, ultra_rare_hit = get_outcome(adjusted_roll, bet_type)
        
        # Snake eyes
        snake_eyes = False
        if base_roll == 0:
            multiplier = 0.0
            snake_eyes = True

        # Calculate winnings
        winnings = round(amount_int * multiplier)
        new_balance = current - amount_int + winnings
        net_gain = winnings - amount_int
        loss_amount = amount_int - winnings
        
        # Special case for "all" bets with 0 multiplier
        dead = (bet_type == "all" and multiplier == 0)
        if dead:
            new_balance = 0  # Lose all cookies

        # Balance update logic
        if new_balance > self.MAX_COOKIES:
            actual_winnings = self.MAX_COOKIES - (current - amount_int)
            actual_net_gain = actual_winnings - amount_int
            
            db_update("cookies",
                    [f"user_id:{user_id}", f"guild_id:{guild_id}"],
                    [("cookies", self.MAX_COOKIES)])
            
            if actual_winnings > 0:
                response = (
                    f"💎💎💎 **YOU WON CAPITALISM!** 💎💎💎\n"
                    f"Your winnings of {winnings} cookies were capped at 1,000,000!\n"
                    f"You received {actual_winnings} cookies instead (Net: +{actual_net_gain})."
                )
            else:
                response = (
                    f"💎💎💎 **YOU WON CAPITALISM!** 💎💎💎\n"
                    f"Your balance was already at 1,000,000 cookies!\n"
                    f"No additional winnings were awarded."
                )
            
            await ctx.send(f"{await author_ping(ctx)} {response}")
            return
        else:
            # Regular update
            db_update("cookies",
                    [f"user_id:{user_id}", f"guild_id:{guild_id}"],
                    [("cookies", new_balance)])

        # Fudge the response to snake eyes if the loss is equal to the pot
        if loss_amount == amount_int:
            if bet_type == "all":
                dead = True
            else:
                snake_eyes = True

        # Response with ORIGINAL MESSAGES
        if dead:
            response = f"🎲 🎲 **SNAKE EYES** - Your cookies have CRUMBLED!! You lost them all! <:cri:1369238296479273042>"
        elif snake_eyes:
            response = f"🎲 🎲 **SNAKE EYES** - You lost {amount_int} cookies!! <:cri:1369238296479273042>"
        elif net_gain > 0:
            if ultra_rare_hit:
                
                if multiplier == 4.0:
                    response = f"💎💎💎 **ULTRA RARE MYTHIC GAMBA** - You won THE HIGHEST PAYOUT with a ``{multiplier}x`` multiplier!!! Net gain: ``{net_gain}`` cookies!"
                
                if multiplier == 3.8:
                    response = f"✨✨✨ **EXTRA RARE SPARKLY GAMBA** - You won THE JACKPOT with a ``{multiplier}x`` multiplier!!! Net gain: ``{net_gain}`` cookies!"
                
                if multiplier == 3.6:
                    response = f"⭐⭐⭐ **RARE GAMBA** - You won THE JACKPOT with a ``{multiplier}x`` multiplier!!! Net gain: ``{net_gain}`` cookies!"
                
                if multiplier == 3.2:
                    response = f"🎉🎉🎉 **EXTRA SPECIAL GAMBA** - You won THE JACKPOT with a ``{multiplier}x`` multiplier!!! Net gain: ``{net_gain}`` cookies!"
                
                if multiplier == 3.0:
                    response = f"7️7️7️ **SPECIAL GAMBA** - You won THE JACKPOT with a ``{multiplier}x`` multiplier!!! Net gain: ``{net_gain}`` cookies!"

            elif multiplier >= 2.0:
                response = f"💰 💰 💰 **JACKPOT** - You WON BIG with a ``{multiplier}x`` multiplier! Net gain: ``{net_gain}`` cookies."
            else:
                response = f"🥳 You won with a ``{multiplier}x`` multiplier! Net gain: ``{net_gain}`` cookies."
        elif net_gain == 0:
            response = f"<:bruh:1371231771462729730> You broke even. You got your ``{amount_int}`` cookies back."
        else:
            response = f"😔 You lost ``{loss_amount}`` cookies!"

        # Final response with current balance
        current = self.check_cookies(guild_id, str(user_id))
        await ctx.send(f"{await author_ping(ctx)} {response} Current cookies: ``{current}``")