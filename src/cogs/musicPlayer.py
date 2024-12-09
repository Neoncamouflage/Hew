import asyncio
import logging
from typing import cast
import random
import json
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import View, Button
from discord import Embed, Interaction
from datetime import datetime, timezone
import uuid
import wavelink
import time
with open('./opts.json', 'r') as opts_file:
    music_opts = json.load(opts_file)

class MusicPlayerView(View):
    def __init__(self, bot: commands.Bot, embed: Embed):
        super().__init__(timeout=None)
        self.bot = bot
        self.embed = embed
        self.startTime = datetime.now(timezone.utc)
        self.id = str(uuid.uuid4())[:8]
        self.player_message = None
        self.thumbPick = random.choice(music_opts['thumb_images'])
        self.station = random.choice(music_opts['names'])
        self.requests = {}
        self.prev = None

    def finish_embed(self):
        endTime = datetime.now(timezone.utc)
        time_difference = endTime - self.startTime
        total_seconds = int(abs(time_difference.total_seconds()))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            formatted_time = f"{hours}h {minutes}m and {seconds}s"
        elif minutes > 0:
            formatted_time = f"{minutes}m and {seconds}s"
        else:
            formatted_time = f"{seconds}s"
        self.embed = discord.Embed()
        self.embed.set_author(name=self.station)
        self.embed.set_thumbnail(url="attachment://"+self.thumbPick)
        self.embed.color = discord.Color.dark_embed()
        self.embed.title = "Off Air"
        self.embed.description = f"Played for {formatted_time}."
        self.embed.set_image(url=music_opts['off_url'])

    def update_embed(self,member=None,player = None,original = None):
        """Update the embed with the current song and player status."""
        self.embed = discord.Embed()
        self.embed.set_author(name=self.station)
        self.embed.set_thumbnail(url="attachment://"+self.thumbPick)
        self.embed.color = discord.Color.orange()
        if player is None:
            print("Off Air 1")
            self.embed.title = "Off Air"
            self.embed.description = "No song is currently playing."
            self.embed.set_image(url=music_opts['off_url'])
        else:
            track = player.current
            if track:
                print("Track",track)
                if self.prev is None:
                    self.prev = track.title
                print("Prev:",self.prev)
                if self.prev and self.prev != track.title:
                    #print("Prev:",self.prev,"Title:",track.title)
                    #print("Prev:",type(self.prev),"Title:",type(track.title))
                    if self.requests.get(self.prev) is not None:
                        del self.requests[self.prev]
                    self.prev = track.title
                requester = self.requests.get(track.title)
                #print(requester)
                if requester is not None:
                    self.embed.set_footer(text="Requested by "+requester.display_name,icon_url=requester.avatar.url)
                elif member is not None:
                    self.embed.set_footer(text="Requested by "+member.display_name,icon_url=member.avatar.url)
                embedTitle = []
                if track.title:
                    embedTitle.append(track.title)
                if track.album.name:
                    embedTitle.append(track.album.name)
                if track.author:
                    embedTitle.append(track.author)
                if len(embedTitle):
                    self.embed.title = "Now Playing:\n"+' - '.join(embedTitle)
                if track.artwork:
                    self.embed.set_image(url=track.artwork)
                else:
                    self.embed.set_image(url=music_opts['missing_url'])
                if original and original.recommended:
                    self.embed.set_footer(text=f'This track was recommended via {track.source}')

                if len(player.queue):
                    queue = []
                    for each in player.queue:
                        queue.append(
                            (each.title if each.title else 'Unknown Title') +
                            ' - ' +
                            (each.author if each.author else 'Unknown Author')
                        )
                    self.embed.add_field(name="Queue", value='\n'.join(queue), inline=False)
            else:
                print("Off Air 2")
                self.embed.title = "Off Air"
                self.embed.description = "No song is currently playing."
                self.embed.set_image(url=music_opts['off_url'])

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.blurple)
    async def toggle_pause(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            print("No Player - Pause/Play Button")
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False)
            return
        await player.pause(not player.paused)
        await interaction.response.edit_message(embed=self.embed, view=self)
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False)

    @discord.ui.button(emoji='⏭️', style=discord.ButtonStyle.blurple)
    async def skip(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False)
            return

        await player.skip(force=True)
        self.update_embed(player=player)
        thumbFile = discord.File('assets/'+self.thumbPick, filename= self.thumbPick )
        await interaction.response.edit_message(embed=self.embed, view=self, attachments=[thumbFile])
        #self.player_message = player_message
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False)

    @discord.ui.button(emoji='❌', style=discord.ButtonStyle.secondary)
    async def quit(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            print("No Player - Quit Button")
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False)
            return
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False)
        if self.bot.playerSessions.get(interaction.guild.id):
            del self.bot.playerSessions[interaction.guild.id]
        await player.disconnect()
        if self.player_message:
            await self.player_message.delete()
        self.stop()
        

    @discord.ui.button(emoji='🔉', style=discord.ButtonStyle.secondary)
    async def volume_down(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            print("No Player - volDown Button")
            if not interaction.response.is_done():
                await interaction.response.send_message("No active player.", ephemeral=True)
            return
        await player.set_volume(player.volume-20)
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False)
    @discord.ui.button(emoji='🔊', style=discord.ButtonStyle.secondary)
    async def volume_up(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            print("No Player - volUp Button")
            if not interaction.response.is_done():
                await interaction.response.send_message("No active player.", ephemeral=True)
            return
        await player.set_volume(player.volume+20)
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False)

    @discord.ui.button(emoji='🔁', style=discord.ButtonStyle.red)
    async def loop(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False)
            return
        if player.queue.mode == wavelink.QueueMode.normal:
            print("NORMAL")
            player.queue.mode = wavelink.QueueMode.loop_all
            button.style = discord.ButtonStyle.green
        else:
            player.queue.mode = wavelink.QueueMode.normal
            button.style = discord.ButtonStyle.red

        self.update_embed(player=player)
        thumbFile = discord.File('assets/'+self.thumbPick, filename= self.thumbPick )
        await interaction.response.edit_message(embed=self.embed, view=self, attachments=[thumbFile])
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False)
    
    @discord.ui.button(emoji='🔎', style=discord.ButtonStyle.red)
    async def autoplay(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False)
            return
        if player.autoplay == wavelink.AutoPlayMode.enabled:
            player.autoplay = wavelink.AutoPlayMode.partial
            button.style = discord.ButtonStyle.red
        else:
            player.autoplay = wavelink.AutoPlayMode.enabled
            button.style = discord.ButtonStyle.green

        self.update_embed(player=player)
        thumbFile = discord.File('assets/'+self.thumbPick, filename= self.thumbPick )
        await interaction.response.edit_message(embed=self.embed, view=self, attachments=[thumbFile])
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False)

    @discord.ui.button(emoji='❔', style=discord.ButtonStyle.secondary)
    async def musicHelp(self, interaction: Interaction, button: Button):
        helpDescription = "Request songs with `/play`. Searches YouTube Music by default, also accepts direct YouTube URLs. Player will disable after no songs are played for 5 minutes, or if all users have left the voice channel."
        helpButtons = {
            "⏯️"     : "Pauses or resumes the current track.",
            "⏭️"     : "Skips the current track",
            "❌"     : "Closes the player and disconnects Hew from the voice channel.",
            "🔉/🔊"  : "Increases or decreases the player volume.",
            "🔁"     : "Continuously loops through the current queue of tracks.\nExperimental feature. May not function perfectly.",
            "🔎"     : "Searches for recommendations to play once the queue ends. Does not work if the queue has already ended.\nExperimental feature. May not function perfectly."

        }
        helpEmbed = discord.Embed(color=discord.Color.blue(),title="Help",description=helpDescription)
        helpEmbed.set_thumbnail(url=music_opts['info_url'])
        helpEmbed.set_footer(text=f"Player ID: {self.id}")
        for button,info in helpButtons.items():
            helpEmbed.add_field(name=button, value=info, inline=True)
        await interaction.response.send_message(embed=helpEmbed,ephemeral=True)

class Music(commands.Cog,):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.playerMonitor.start()

    @tasks.loop(seconds=60)
    async def playerMonitor(self):
        #print("Looping",datetime.now())
        uuidA = str(uuid.uuid4())[:8]
        for guildID in list(self.bot.playerSessions.keys()):
            view = self.bot.playerSessions.get(guildID)
            #print("Checking for ID",uuidA)
            #print("GUILDID",guildID)
            guild = self.bot.get_guild(guildID)
            #print("GUILD",guild)
            if guild.voice_client:
                player: wavelink.Player = cast(wavelink.Player, guild.voice_client)
                if player and len(player.queue) == 0 and player.current is None and player.autoplay != wavelink.AutoPlayMode.enabled:
                    if view.offlineTime and time.time() - view.offlineTime > 300:
                        view.finish_embed()
                        thumbFile = discord.File('assets/'+view.thumbPick, filename= view.thumbPick )
                        view.clear_items()
                        if view.player_message:
                            await view.player_message.edit(embed=view.embed, view=view, attachments=[thumbFile])       
                        view.stop()
                        del self.bot.playerSessions[guildID]
                        await player.disconnect()
                        print("Player Idle Loop - Disconnected")            
            else:
                print("No voice client in guild",guild)
    
    @app_commands.command(name="play", description = "Adds a song to the queue and creates a music player if needed.")
    async def play(self, interaction: discord.Interaction, *, song: str) -> None:
        """Play a song with the given query."""
        if not interaction.guild:
            return
        member = interaction.user
        player: wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)  # type: ignore
        view = self.bot.playerSessions.get(interaction.guild.id)
        if view is None:
            print("Creating new View")
            view = MusicPlayerView(self.bot,discord.Embed())
            self.bot.playerSessions[interaction.guild.id] = view
        if not player:
            print("No Player - Play Command")
            try:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)  # type: ignore
                player.autoplay = wavelink.AutoPlayMode.partial
                player.inactive_channel_tokens = 1
            except AttributeError:
                await interaction.response.send_message("Please join a voice channel first before using this command.",ephemeral=True)
                return
            except discord.ClientException:
                await interaction.response.send_message("I was unable to join this voice channel. Please try again.",ephemeral=True)
                return

        # Lock the player to this channel...
        if not hasattr(player, "home"):
            player.home = interaction.channel
        elif player.home != interaction.channel:
            await interaction.response.send_message(f"You can only play songs in {player.home.mention}, as the music player has already started there. To choose a new channel, close the old player first.",ephemeral=True)
            return

        # This will handle fetching Tracks and Playlists...
        # Seed the doc strings for more information on this method...
        # If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
        # Defaults to YouTube for non URL based queries...
        tracks: wavelink.Search = await wavelink.Playable.search(song)
        if not tracks:
            await interaction.response.send_message(f"{interaction.user.mention} - No search results for that, sorry.",ephemeral=True)
            return

        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            added: int = await player.queue.put_wait(tracks)
            await interaction.response.send_message(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.",ephemeral=True)
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await interaction.response.send_message(f"Added **`{track}`** to the queue.",ephemeral=True)
            view.requests[track.title] = member
        if player.playing:
            view.update_embed(player=player,original = None)
            thumbFile = discord.File('assets/'+view.thumbPick, filename= view.thumbPick )
            if view.player_message:
                await view.player_message.edit(embed=view.embed, view=view, attachments=[thumbFile])
            else:
                player_message = await player.home.send(embed=view.embed, view=view, file=thumbFile)
                print("New player - Play Command",player_message)
                view.player_message = player_message
        else:
            await player.play(player.queue.get(), volume=30)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))