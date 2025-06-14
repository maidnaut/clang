import discord, asyncio, os, re, random
from inc.utils import *
from inc.db import *
from discord.ext import commands
from collections import defaultdict, deque
from profanity_check import predict, predict_prob

def setup(bot):
    bot.add_cog(MarkovCog(bot))

class MarkovCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chains = defaultdict(lambda: defaultdict(list))
        self.key_order = defaultdict(deque)
        self.data_dir = "inc/markov"
        self.MAX_ENTRIES = 50000
        
        os.makedirs(self.data_dir, exist_ok=True)
        self.load_all_chains()

        self.save_interval = 300 # 5 minute autosave
        self.bg_task = self.bot.loop.create_task(self.auto_save())

        if not table_exists("markov_optout"):
            new_db("markov_optout", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("user_id", "INTEGER"),
            ])

        self.__help__ = {
            "markov": {
                "args": "on, off",
                "desc": "Opts in or out of markov chain training",
                "perm": "everyone"
            },
        }



    # Get the filepath
    def get_chain_path(self, guild_id):
        return os.path.join(self.data_dir, f"{guild_id}.txt")

    # Autosave
    async def auto_save(self):

        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            await asyncio.sleep(self.save_interval)
            for guild_id in self.chains:
                
                path = self.get_chain_path(guild_id)
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        for key in list(self.key_order[guild_id])[-self.MAX_ENTRIES:]:
                            values = self.chains[guild_id].get(key, [])
                            line = f"{' '.join(key)}|{','.join(values)}\n"
                            f.write(line)
                except Exception as e:
                    print(f"Error saving chain for guild {guild_id}: {e}")

    # Load everything at startup
    def load_all_chains(self):

        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".txt"):

                    try:
                        guild_id = int(filename[:-4])
                        self.load_chain(guild_id)
                    except (ValueError, IndexError):
                        continue
                        
        except FileNotFoundError:
            pass

    # Load the guild's specific chain
    def load_chain(self, guild_id):
        path = self.get_chain_path(guild_id)
        if not os.path.exists(path):
            return
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        key_part, values_part = line.split("|", 1)
                        key = tuple(key_part.split())
                        values = values_part.split(",")
                        
                        if len(self.key_order[guild_id]) < self.MAX_ENTRIES:
                            self.chains[guild_id][key] = values
                            self.key_order[guild_id].append(key)
                        else:
                            break
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error loading chain for guild {guild_id}: {e}")




    # Add to the chain
    async def train_markov(self, message):
        if not message.guild or message.author.bot:
            return

        opted_out = db_read("markov_optout", [f"user_id:{message.author.id}"])
        if opted_out:
            return

        guild_id = message.guild.id

        # Block private category logging
        ticket_category = await get_channel(guild_id, "ticket_category")
        jail_category = await get_channel(guild_id, "jail_category")
        mod_category = await get_channel(guild_id, "mod_category")

        private_categories = []
        if ticket_category:
            private_categories.append(ticket_category.id)
        if jail_category:
            private_categories.append(jail_category.id)
        if mod_category:
            private_categories.append(mod_category.id)

        # Drop out if it's a private category
        if message.channel.category_id in private_categories:
            return

        # Remove mentions and channels
        clean_content = re.sub(r'<@!?\d+>', '', message.content)
        clean_content = re.sub(r'<@&\d+>', '', clean_content)
        clean_content = re.sub(r'<#\d+>', '', clean_content).strip()
        
        if not clean_content or predict([clean_content])[0] == 1:
            return

        # Bump it in
        words = clean_content.split()
        if len(words) < 3:
            return

        # Init guild data
        if guild_id not in self.chains:
            self.chains[guild_id] = {}
        if guild_id not in self.key_order:
            self.key_order[guild_id] = deque()

        for i in range(len(words) - 2):
            key = (words[i], words[i+1])
            
            if key not in self.chains[guild_id]:
                self.chains[guild_id][key] = []
                
            self.chains[guild_id][key].append(words[i+2])
            
            # Add to key_order if new key
            if key not in self.key_order[guild_id]:
                self.key_order[guild_id].append(key)
                
                # Max entries = 50k - remove old keys
                while len(self.key_order[guild_id]) > self.MAX_ENTRIES:
                    oldest_key = self.key_order[guild_id].popleft()
                    
                    if oldest_key in self.chains[guild_id]:
                        del self.chains[guild_id][oldest_key]




    # Generate a response
    def generate_response(self, guild_id, seed_words=None, original_msg=None):
        chain = self.chains[guild_id]
        if not chain:
            return "clang not know words"

        keys = list(chain.keys())
        attempts = 0
        max_attempts = 5
        response = ""

        original_msg = original_msg.lower().strip() if original_msg else ""

        while attempts < max_attempts:
            attempts += 1

            if seed_words and len(seed_words) > 1:
                key = (seed_words[0], seed_words[1])
                if key not in chain:
                    key = random.choice(keys)
            else:
                key = random.choice(keys)

            # 50% chance to ignore seed or pick a new response
            if random.random() < 0.5:
                key = random.choice(keys)

            words = list(key)
            while True:
                next_words = chain.get(key)
                if not next_words:
                    break

                next_word = random.choice(next_words)
                words.append(next_word)
                key = (key[1], next_word)

                if len(words) > 20 or random.random() < 0.1:
                    break

            response = ' '.join(words)

            if not original_msg or response.lower().strip() != original_msg:
                break

        return response or "clang confused"





    # respond on reply
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.content:
            return

        if message.guild:
            await self.train_markov(message)

        if self.bot.user in message.mentions:
            if not message.guild:
                return
                
            guild_id = message.guild.id
            clean_content = re.sub(rf'<@!?{self.bot.user.id}>', '', message.content).strip()
            seed_words = clean_content.split()[:2] if clean_content else None
            
            response = self.generate_response(guild_id, seed_words, original_msg=message.content)
            
            ctx = await self.bot.get_context(message)
            await message.channel.send(f"{await user_ping(ctx, message.author)} {response}")





    # Markov opt out
    @commands.command()
    async def markov(self, ctx, mode: str = None):
        if mode == "off":
            db_insert("markov_optout", ["user_id"], [str(ctx.author.id)])
            await ctx.send(f"{await user_ping(ctx, ctx.author)} You’re now opted out of Markov chain logging.")
        elif mode == "on":
            db_remove("markov_optout", ["user_id"], [str(ctx.author.id)])
            await ctx.send(f"{await user_ping(ctx, ctx.author)} You’re now opted back in to Markov chain logging.")
        else:
            await ctx.send(f"{await user_ping(ctx, ctx.author)} Usage: `!markov on` or `!markov off`")
