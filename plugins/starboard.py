import discord, asyncio
from discord.ext import commands
from inc.utils import *
from inc.db import *

def setup(bot):
    bot.add_cog(StarboardCog(bot))

class StarboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scan_lock = asyncio.Lock()  # Prevent multiple concurrent scans
        
        self.__help__ = {
            "starboard": {
                "args": "[status|set_emoji|set_threshold|set_channel|scan]",
                "desc": "Configure and manage the starboard system",
                "perm": "admin"
            },
            "starboard set_emoji": {
                "args": "<emoji>",
                "desc": "Set the emoji for starboard reactions",
                "perm": "admin"
            },
            "starboard set_threshold": {
                "args": "<number>",
                "desc": "Set minimum stars required",
                "perm": "admin"
            },
            "starboard set_channel": {
                "args": "<#channel>",
                "desc": "Set starboard destination channel",
                "perm": "admin"
            },
            "starboard scan": {
                "args": "[limit]",
                "desc": "Scan recent messages for stars",
                "perm": "admin"
            }
        }

        if not table_exists("starboard_config"):
            new_db("starboard_config", [
                ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                ("guild_id", "INTEGER"),
                ("emoji", "TEXT"),
                ("threshold", "INTEGER"),
                ("channel_id", "TEXT"),
            ])

    # Database helper methods
    def get_starboard_config(self, guild_id):
        return db_read("starboard_config", [f"guild_id:{guild_id}"]) or {
            "emoji": "⭐",
            "threshold": 3,
            "channel_id": None
        }

    def save_starboard_config(self, guild_id, config):
        db_write("starboard_config", [f"guild_id:{guild_id}"], config)

    def get_starboard_message(self, original_id):
        return db_read("starboard_posts", [f"original_id:{original_id}"])

    def save_starboard_message(self, original_id, starboard_id, channel_id):
        db_write("starboard_posts", [f"original_id:{original_id}"], {
            "starboard_id": starboard_id,
            "channel_id": channel_id
        })

    def delete_starboard_message(self, original_id):
        db_write("starboard_posts", [f"original_id:{original_id}"], None)

    # Starboard core functionality
    async def process_starboard(self, payload, added=True):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        config = self.get_starboard_config(guild.id)
        if not config or not config.get("channel_id"):
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel or channel.id == config["channel_id"]:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return

        # Count relevant reactions
        star_count = 0
        for reaction in message.reactions:
            if str(reaction.emoji) == config["emoji"]:
                star_count = reaction.count
                break

        # Handle starboard post
        starboard_post = self.get_starboard_message(message.id)
        starboard_channel = guild.get_channel(config["channel_id"])
        
        if not starboard_channel:
            return

        # Create/update starboard message
        if star_count >= config["threshold"]:
            embed = discord.Embed(
                description=message.content,
                color=discord.Color.gold(),
                timestamp=message.created_at
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url
            )
            embed.add_field(
                name="Source",
                value=f"[Jump to Message]({message.jump_url})",
                inline=False
            )
            embed.set_footer(text=f"⭐ {star_count} | ID: {message.id}")
            
            # Add image if exists
            if message.attachments:
                image = message.attachments[0]
                if image.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp')):
                    embed.set_image(url=image.url)
            
            if starboard_post:
                try:
                    star_msg = await starboard_channel.fetch_message(starboard_post["starboard_id"])
                    await star_msg.edit(embed=embed)
                except:
                    self.delete_starboard_message(message.id)
            else:
                star_msg = await starboard_channel.send(embed=embed)
                self.save_starboard_message(message.id, star_msg.id, starboard_channel.id)
        
        # Remove starboard entry if below threshold
        elif starboard_post:
            try:
                star_msg = await starboard_channel.fetch_message(starboard_post["starboard_id"])
                await star_msg.delete()
            except:
                pass
            self.delete_starboard_message(message.id)

    # Event listeners
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        await self.process_starboard(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.process_starboard(payload, added=False)

    # Starboard commands
    @commands.group()
    async def starboard(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.starboard_status(ctx)

    async def cog_check(self, ctx):
        user_level = await get_level(ctx)
        if user_level >= 4 or ctx.author == ctx.guild.owner:
            return True
        await ctx.send(f"{await author_ping(ctx)} You don't have permission to manage starboard!")
        return False

    @starboard.command(name="status")
    async def starboard_status(self, ctx):
        config = self.get_starboard_config(ctx.guild.id)
        channel = ctx.guild.get_channel(config["channel_id"]) if config["channel_id"] else None
        
        embed = discord.Embed(
            title="⭐ Starboard Configuration",
            color=discord.Color.blue()
        )
        embed.add_field(name="Emoji", value=config["emoji"], inline=True)
        embed.add_field(name="Threshold", value=config["threshold"], inline=True)
        embed.add_field(name="Channel", value=channel.mention if channel else "Not set", inline=True)
        
        await ctx.send(embed=embed)

    @starboard.command(name="set_emoji")
    async def set_emoji(self, ctx, emoji: str):
        config = self.get_starboard_config(ctx.guild.id)
        config["emoji"] = emoji
        self.save_starboard_config(ctx.guild.id, config)
        await ctx.send(f"{await author_ping(ctx)} Starboard emoji set to {emoji}")

    @starboard.command(name="set_threshold")
    async def set_threshold(self, ctx, threshold: int):
        if threshold < 1:
            return await ctx.send(f"{await author_ping(ctx)} Threshold must be at least 1")
            
        config = self.get_starboard_config(ctx.guild.id)
        config["threshold"] = threshold
        self.save_starboard_config(ctx.guild.id, config)
        await ctx.send(f"{await author_ping(ctx)} Starboard threshold set to {threshold}")

    @starboard.command(name="set_channel")
    async def set_channel(self, ctx, channel: discord.TextChannel):
        config = self.get_starboard_config(ctx.guild.id)
        config["channel_id"] = channel.id
        self.save_starboard_config(ctx.guild.id, config)
        await ctx.send(f"{await author_ping(ctx)} Starboard channel set to {channel.mention}")

    @starboard.command(name="scan")
    async def scan_backlog(self, ctx, limit: int = 1000):
        if self.scan_lock.locked():
            return await ctx.send(f"{await author_ping(ctx)} Another scan is already in progress")
            
        async with self.scan_lock:
            config = self.get_starboard_config(ctx.guild.id)
            if not config or not config.get("channel_id"):
                return await ctx.send(f"{await author_ping(ctx)} Starboard not configured. Set a channel first!")
            
            await ctx.send(f"{await author_ping(ctx)} Scanning last {limit} messages...")
            processed = 0
            found = 0
            
            for channel in ctx.guild.text_channels:
                if not channel.permissions_for(ctx.guild.me).read_message_history:
                    continue
                    
                try:
                    async for message in channel.history(limit=limit):
                        # Check if message has our emoji
                        for reaction in message.reactions:
                            if str(reaction.emoji) == config["emoji"]:
                                await self.process_starboard(discord.RawReactionActionEvent(
                                    {
                                        "message_id": message.id,
                                        "channel_id": channel.id,
                                        "guild_id": ctx.guild.id,
                                        "user_id": self.bot.user.id,
                                        "emoji": reaction.emoji
                                    },
                                    "REACTION_ADD"
                                ))
                                found += 1
                                break
                        processed += 1
                except Exception as e:
                    await ctx.send(f"{await author_ping(ctx)} Error scanning {channel.mention}: {str(e)}")
            
            await ctx.send(f"{await author_ping(ctx)} Scan complete! Processed {processed} messages, found {found} starred messages")