import asyncio
import logging
from typing import cast
import random
import json
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from discord import Embed, Interaction
from datetime import datetime, timezone
import uuid
import wavelink
with open('./opts.json', 'r') as opts_file:
    music_opts = json.load(opts_file)

class MusicPlayerView(View):
    def __init__(self, bot: commands.Bot, embed: Embed):
        super().__init__(timeout=None)
        self.bot = bot
        self.embed = embed
        self.startTime = datetime.now(timezone.utc)
        self.id = str(uuid.uuid4())[:13]
        self.player_message = None
        self.thumbPick = random.choice(music_opts['thumb_images'])
        self.station = random.choice(music_opts['names'])
        self.requests = {}

    def update_embed(self,member=discord.Member,player = None,original = None):
        """Update the embed with the current song and player status."""
        self.embed = discord.Embed()
        self.embed.set_author(name=self.station)
        self.embed.timestamp = self.startTime
        self.embed.set_thumbnail(url="attachment://"+self.thumbPick)
        self.embed.color = discord.Color.orange()
        if player is None:
            self.embed.title = "Off Air"
            self.embed.description = "No song is currently playing."
            self.embed.set_image(url=music_opts['off_url'])
        else:
            track = player.current
            if track:
                requester = self.requests.get(track.title)
                if requester is not None:
                    self.embed.set_footer(text="Requested by "+requester.display_name,icon_url=requester.avatar.url)
                    del self.requests[track.title]
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
                    self.embed.title = "Now Playing: "+' - '.join(embedTitle)
                if track.artwork:
                    self.embed.set_image(url=track.artwork)
                else:
                    self.embed.set_image(url=music_opts['missing_url'])
                if original and original.recommended:
                    self.embed.description += f"\n\n`This track was recommended via {track.source}`"

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
                self.embed.title = "Off Air"
                self.embed.description = "No song is currently playing."
                self.embed.set_image(url=music_opts['off_url'])

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.blurple)
    async def toggle_pause(self, interaction: Interaction, button: Button):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            print("No Player - Pause/Play Button")
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False)
            return
        await player.pause(not player.paused)
        if player.paused:
            button.emoji = "▶️"
        else:
            button.emoji = "⏸️"
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

    


class Music(commands.Cog,):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
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
            except AttributeError:
                await interaction.response.send_message("Please join a voice channel first before using this command.",ephemeral=True)
                return
            except discord.ClientException:
                await interaction.response.send_message("I was unable to join this voice channel. Please try again.",ephemeral=True)
                return

        # Turn on AutoPlay to enabled mode.
        # enabled = AutoPlay will play songs for us and fetch recommendations...
        # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
        # disabled = AutoPlay will do nothing...
        #player.autoplay = wavelink.AutoPlayMode.partial

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
        if not player.playing:
            # Play now since we aren't playing anything...
            await player.play(player.queue.get(), volume=30)
        view.update_embed(member=member,player=player)
        thumbFile = discord.File('assets/'+view.thumbPick, filename= view.thumbPick )
        if view.player_message:
            await view.player_message.edit(embed=view.embed, view=view, attachments=[thumbFile])
        else:
            player_message = await player.home.send(embed=view.embed, view=view, file=thumbFile)
            view.player_message = player_message

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))