### Prerequisites
- Python 3.7+
- `discord.py` library
- `yt-dlp` library
- FFmpeg (for audio processing)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/em1ru/YtMusicDiscordBot.git

2. Install the required libraries:
```bash
pip install discord.py yt-dlp
```
3. Set your Discord bot token as an environment variable:

    On Linux/MacOS:
    ```bash
    export DISCORD_BOT_TOKEN="your-token-here"
    ```
    On Windows:
    ```bash
    set DISCORD_BOT_TOKEN=your-token-here
    ```
4. Run the bot:
```bash
python music_bot.py
```
### Usage

!play <YouTube URL or search query>: Play a song or add it to the queue.
!skip: Skip the current song.
!stop: Stop playback and clear the queue.
