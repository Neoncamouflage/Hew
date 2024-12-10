import discord
import asyncio
import os
import json
from typing import cast
from typing import Literal, Optional
from discord.ext import commands
import datetime
import wavelink # type: ignore
import paramiko
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
        self.bot.unloadedCogs = []
        newLoaded = []
        for cog in os.listdir(".\\cogs"):
            if cog.endswith(".py"):
                if cog in self.bot.loadedCogs:
                    try:
                        cogName = f"cogs.{cog.replace('.py', '')}"
                        await self.bot.reload_extension(cogName)
                        newLoaded.append(cog)
                        reloads +=(cogName+'\n')
                    except Exception as e:
                        self.bot.unloadedCogs.append(cog)
                        print(e)
                else:
                    try:
                        await self.bot.load_extension(f"cogs.{cog[:-3]}")
                        newLoaded.append(cog)
                        reloads +=(f"cogs.{cog.replace('.py', '')}"+'\n')
                    except Exception as e:
                        self.bot.unloadedCogs.append(cog)
                        print(e)
        self.bot.loadedCogs = [a for a in newLoaded]
        await ctx.send(reloads+'Reloaded')

    @commands.command()
    async def help(self,ctx):
        content = 'HewV2 is currently in development and all commands are migrating from prefixes to slash commands. Available commands can be found by typing `/`. If a command does not appear, it is not available for use.\n\nAll slash commands have a ❔ button for context specific instructions. If you\'ve encountered a critical error or bug, please reach out to Neoncamouflage.'
        content += '\n\nKnown Issues - Music Player:\n- Spotify not yet supported, results in an error.\n- Age Restricted content not yet supported, results in silence until skipped.'
        await ctx.send(content)

    @commands.command()
    async def status(self,ctx):
        embed = discord.Embed()
        embed.title = "Hew - Version "+config['version']
        elapsed_time = datetime.datetime.now() - self.bot.start_time
        days = elapsed_time.days
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days > 0:
            formatted_time = f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            formatted_time = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            formatted_time = f"{minutes}m {seconds}s"
        else:
            formatted_time = f"{seconds}s"
        
        embed.add_field(name="Guilds", value='\n'.join([str(a.id) for a in self.bot.guilds]), inline=True)
        embed.add_field(name="Cogs", value='\n'.join(['🟢 '+f"cogs.{a.replace('.py', '')}" for a in self.bot.loadedCogs]+['🔴 '+f"cogs.{a.replace('.py', '')}" for a in self.bot.unloadedCogs]), inline=True)
        embed.add_field(name="Uptime", value=formatted_time, inline=True)
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
    @commands.command()
    async def logs(self,ctx):
        embed2 = discord.Embed()
        embed2.title = "LavaLink Server Logs"
        ssh_host = config['ssh_target']
        ssh_port = 22
        ssh_user = config["ssh_user"]
        ssh_password = config['ssh_pass']
        log_path = config["log_path"]
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)

            command = f"tail -n 10 {log_path}"
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            ssh.close()
            desc = []
            total = 0
            if error:
                await ctx.send(f"Error fetching logs: {error}")
            else:
                lines = output.split('\n')
                for line in reversed(lines):
                    if total+len(line)+1 < 4000:
                        desc.append(line)
                        total += len(line)+1
                    else:
                        break
                desc.reverse()
                embed2.description = '\n'.join(desc)
            await ctx.send(embed=embed2)
                
        except Exception as e:
            await ctx.send(f"Failed to retrieve logs: {str(e)}. Log length: {len(output)}")



async def setup(bot):
    await bot.add_cog(Moderation(bot))