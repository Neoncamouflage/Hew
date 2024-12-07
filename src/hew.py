#! python3
import discord
import asyncio
import os
from discord.ext import commands
import logging

def get_prefix(bot, message):
    prefixes = ['Hew ','hew ','Hew, ','hew, ']
    if message.channel.type is discord.ChannelType.private:
        print("Yes")
        return commands.when_mentioned_or(*prefixes)(bot, message)
    if message.channel.name in ["test001",'hewbris']:
        return '!'
    return commands.when_mentioned_or(*prefixes)(bot, message)

discord.utils.setup_logging()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = get_prefix,description="A DnD flavored Discord bot",intents=intents)

@bot.command()
async def reload(ctx):
    for cog in os.listdir(".\\cogs"):
        if cog.endswith(".py"):
            try:
                cog = f"cogs.{cog.replace('.py', '')}"
                await bot.reload_extension(cog)
            except Exception as e:
                print(f'{cog} cannot be loaded:')
                raise e

async def load_extensions():
    for filename in os.listdir(".\\cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start('NzAwMDc5NTE1NTU2MzgwNzU1.GRKA8G.C6pf__ObKqjSxTYmP242jtbPzkuKeR1uc5Fqak')

asyncio.run(main())