import discord
import asyncio
import os
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def clearmess(self,ctx, amount=5):
        channel = ctx.message.channel
        await channel.purge(limit=int(amount) + 1)
        await ctx.send(f"All set, deleted {amount} messages")

    @commands.command()
    async def report(self,ctx,*,content):
        if ctx.channel.type is discord.ChannelType.private:
            adminChat = self.bot.get_channel(772305372416311327)
            await adminChat.send(f'<@&732693073649467403>\nReport filed:\n{content}')

    @commands.command()
    async def copy(self,ctx,limit = None):
        messages = await ctx.channel.history(limit=limit).flatten()
        with open("channel_messages.txt", "a+", encoding="utf-8") as f:
            print(*messages, sep="\n\n<|endoftext|>\n\n", file=f)




async def setup(bot):
    await bot.add_cog(Moderation(bot))