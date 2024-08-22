import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

# Configure the bot
intents = discord.Intents.default()
intents.message_content = True  # Needed for reading messages
bot = commands.Bot(command_prefix='!', intents=intents)

# YouTube download options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # Bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Music Queue
music_queue = []

@bot.command(name='play', help='To play song')
async def play(ctx, *, url):
    try:
        # Auto-join voice channel if not already connected
        if not ctx.voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
            else:
                await ctx.send(f"{ctx.author.name} is not connected to a voice channel")
                return

        # Add song to queue
        music_queue.append(url)
        if len(music_queue) == 1:
            await play_next(ctx)
        else:
            await ctx.send(f'**Added to queue:** {url}')
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

async def play_next(ctx):
    if len(music_queue) > 0:
        url = music_queue[0]
        try:
            server = ctx.guild
            voice_channel = server.voice_client

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
                voice_channel.play(player, after=lambda e: check_queue(ctx))

            await ctx.send(f'**Now playing:** {player.title}')
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

def check_queue(ctx):
    music_queue.pop(0)
    if len(music_queue) > 0:
        bot.loop.create_task(play_next(ctx))

@bot.command(name='stop', help='Stops the song and clears the queue')
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    music_queue.clear()
    await ctx.send("Playback stopped and queue cleared.")

@bot.command(name='skip', help='Skips the current song')
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    await ctx.send("Song skipped.")

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name}')

# Get the token from the environment variable
token = os.getenv('DISCORD_BOT_TOKEN')

if token:
    bot.run(token)
else:
    print("Error: Discord bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
