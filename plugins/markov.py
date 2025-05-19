import os, re, random
from collections import defaultdict

class MarkovCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.chains = defaultdict(lambda: defaultdict(list))
        self.data_dir = "inc/markov"
        self.load_all_chains()
        os.makedirs(self.data_dir, exist_ok=True)

        # Autosave
        self.save_interval = 300 # 5 minutes
        self.bg_task = self.bot.loop.create_task(self.auto_save())




    # Chain management
    def get_chain_path(self, guild_id):
        return os.path.join(self.data_dir, f"{guild_id}.txt")

    # Autosave
    async def auto_save(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            await asyncio.sleep(self.save_interval)

            for guild_id in self.chains:

                path = self.get_chain_path(guild_id)

                with open(path, "w", encoding="utf-8") as f:
                    for key, values in self.chains[guild_id].items():
                        line = f"{' '.join(key)}|{','.join(values)}\n"
                        f.write(line)

    # Initial load
    def load_chain(self, guild_id):
        path = self.get_chain_path(guild_id)
        if not os.path.exists(path):
            return
            
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                key_part, values_part = line.split("|", 1)
                key = tuple(key_part.split())
                values = values_part.split(",")
                self.chains[guild_id][key] = values




    # Add to the chain
    async def train_markov(self, message):

        if not message.guild:
            return
            
        guild_id = message.guild.id
        words = message.content.split()
        
        if len(words) < 3:
            return
            
        for i in range(len(words) - 2):
            self.chains[guild_id][(words[i], words[i+1])].append(words[i+2])




    # Generate a response
    def generate_response(self, guild_id, seed_words=None):
        
        chain = self.chains[guild_id]
        
        # Users need to talk more
        if not chain:
            return "clang not know words"
        
        # Format the seeds from the chain
        if seed_words:
            try:
                key = (seed_words[0], seed_words[1]) if len(seed_words) > 1 else random.choice(list(chain.keys()))
                if key not in chain:
                    key = random.choice(list(chain.keys()))
            except:
                key = random.choice(list(chain.keys()))
        else:
            key = random.choice(list(chain.keys()))
        
        # Generate the response
        response = list(key)
        while True:
            next_words = chain.get(key, None)
            if not next_words:
                break
            next_word = random.choice(next_words)
            response.append(next_word)
            key = (key[1], next_word)
            if len(response) > 20 or random.random() < 0.1:
                break
        return ' '.join(response)




    # respond on reply
    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.author.bot or not message.content:
            return

        if message.guild:
            await self.train_markov(message)

        # check if clang is mentioned
        if self.bot.user in message.mentions:

            # ignore dm's
            if not message.guild:
                return
                
            guild_id = message.guild.id
            
            # strip out clang's mention
            clean_content = re.sub(rf'<@!?{self.bot.user.id}>', '', message.content).strip()
            seed_words = clean_content.split()[:2] if clean_content else None
            
            response = self.generate_response(guild_id, seed_words)
            await message.channel.send(response)