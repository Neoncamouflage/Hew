#! python3
from typing import Literal, Optional
from typing import cast
import discord
import asyncio
import os
import datetime
from discord import app_commands
from discord.ext import commands
import logging
import json
import wavelink # type: ignore
import time


'''
To Do:
Fully set up logging
Turning on auto play while on dead air should immediately find a song
Once the queue gets so long, append ...x more to keep length reasonable.
Back button since the player keeps a history.
'''

with open('./config.json', 'r') as config_file:
    config = json.load(config_file)

def get_prefix(bot, message):
    prefixes = ['Hew ','hew ','Hew, ','hew, ']
    return commands.when_mentioned_or(*prefixes)(bot, message)

discord.utils.setup_logging()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, description="A DnD flavored Discord bot",intents=intents, activity = discord.Game(name="Dungeons and Dragons"), help_command=None)
        self.loadedCogs = []
        self.unloadedCogs = []
        self.playerSessions = {}

    async def setup_hook(self) -> None:
        node: wavelink.Node = wavelink.Node(uri=config['uri'], password=config['lavaPass'])
        await wavelink.Pool.connect(client=self, nodes=[node])
        self.playerNode = node
        await self.load_extensions()
        print("Cogs loaded:",self.loadedCogs)

    async def on_ready(self) -> None:
        print(f'Logged in {self.user} | {self.user.id}')
        
        

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        print("Wavelink Node connected: %r | Resumed: %s", payload.node, payload.resumed)

    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        print("Inactive player!")
        await asyncio.sleep(2)
        home = player.home
        if self.playerSessions.get(home.guild.id):
            view = self.playerSessions[home.guild.id]
            view.finish_embed()
            thumbFile = discord.File('assets/'+view.thumbPick, filename= view.thumbPick )
            view.clear_items()
            if view.player_message:
                await view.player_message.edit(embed=view.embed, view=view, attachments=[thumbFile])       
            view.stop()
            del self.playerSessions[home.guild.id]
        await player.disconnect()
        print("Disconnected")            

    #Need proper handling of this at some point
    async def on_wavelink_track_stuck(self, payload: wavelink.TrackStuckEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        track: wavelink.Playable = payload.track
        print("STUCK")
        print(player)
        print(track)

    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track
        if not player:
            print("NOT PLAYER -Err!")
            return
        view = self.playerSessions.get(player.guild.id)
        if view is None:
            print("ERR - No Guild ID!",dir(player))
            return
        view.update_embed(player=player,original = original)
        thumbFile = discord.File('assets/'+view.thumbPick, filename= view.thumbPick )
        if view.player_message:
            await view.player_message.edit(embed=view.embed, view=view, attachments=[thumbFile])
            print('\nVolume:',view.volume)
        else:
            player_message = await player.home.send(embed=view.embed, view=view, file=thumbFile)
            print("New player - Track start",player_message)
            view.player_message = player_message

    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            print("No player - track end event")
            return
        print("Queue",str(player.queue))
        print("Current",player.current)
        if len(player.queue) == 0 and player.current is None and player.autoplay != wavelink.AutoPlayMode.enabled:
            view = self.playerSessions.get(player.guild.id)
            if view is None:
                print("ERR - No Guild ID! - track end event",dir(player))
                return
            view.offlineTime = time.time()
            view.update_embed(player=player,original = None)
            thumbFile = discord.File('assets/'+view.thumbPick, filename= view.thumbPick )
            if view.player_message:
                await view.player_message.edit(embed=view.embed, view=view, attachments=[thumbFile])
            #else:
                #player_message = await player.home.send(embed=view.embed, view=view, file=thumbFile)
                #print("New player - Track end",player_message)
                #view.player_message = player_message


    async def load_extensions(self):
        for filename in os.listdir(".\\cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    self.loadedCogs.append(filename)
                except Exception as e:
                    self.unloadedCogs.append(filename)


bot = Bot()

async def main():
    async with bot:
        bot.start_time = datetime.datetime.now()
        print("Hew is awake")
        await bot.start(config['discord_key'])


asyncio.run(main())