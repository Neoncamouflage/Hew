import discord
import asyncio
import os
import json
from typing import cast
from typing import Literal, Optional
from discord.ext import commands
import datetime
import wavelink
with open('./config.json', 'r') as config_file:
    config = json.load(config_file)

class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            attempted_command = ctx.invoked_with
            if attempted_command.lower() in ['play']:
                await ctx.send("I've had an upgrade! Prefix commands are out, slash commands are in. Just type a `/` to see what commands are available.")
        else:
            raise error

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self,ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        print("Attempting sync!")
        if not guilds:
            print("Not guild")
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            print("End of not guilds")
            print(synced)
            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return
        print("In between")
        ret = 0
        for guild in guilds:
            print("Guild loop!")
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.command()
    async def reload(self,ctx):
        reloads = ''
        for cog in os.listdir(".\\cogs"):
            if cog.endswith(".py"):
                if cog in self.bot.loadedCogs:
                    try:
                        cog = f"cogs.{cog.replace('.py', '')}"
                        await self.bot.reload_extension(cog)
                        reloads +=(cog+'\n')
                    except Exception as e:
                        print(f'{cog} cannot be loaded:')
                        raise e
                else:
                    await self.bot.load_extension(f"cogs.{cog[:-3]}")
                    self.bot.loadedCogs.append(cog)
        await ctx.send(reloads+'Reloaded')

    @commands.command()
    async def status(self,ctx):
        embed = discord.Embed()
        embed.title = "Hew - Version "+config['version']
        embed.add_field(name="Uptime", value=datetime.datetime.now() - self.bot.start_time, inline=False)
        embed.add_field(name="Cogs", value='\n'.join(self.bot.loadedCogs), inline=True)
        embed.add_field(name="Relay Node", value=f"ID: {self.bot.playerNode.identifier}\nStatus: {self.bot.playerNode.status.name}\nActive Players: {len(self.bot.playerNode.players)}",inline=True)
        count=0
        for k,v in self.bot.playerSessions.items():
            count += 1
            sessions = ""
            guild = self.bot.get_guild(k)
            sessions+=f'Guild: {k}/{guild.name} - View: {v.id} - mID: {v.player_message.id}\nStartTime: {v.startTime}\n'
            if guild.voice_client:
                player: wavelink.Player = cast(wavelink.Player, guild.voice_client)
                if player:
                    sessions+=f'{player.autoplay}\n{player.queue.mode}'
            embed.add_field(name=f"Session {count}", value=sessions, inline=False)
        await ctx.send(embed=embed)




async def setup(bot):
    await bot.add_cog(Moderation(bot))