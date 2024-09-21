import discord #library
from discord.ext import commands #library
import yt_dlp #library
import asyncio #library
intents = discord.Intents.default() #discrod settings
intents.message_content = True
intents.voice_states = True
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'simulate': 'True'} #ytdlp settings
ffmpeg_options = {'options': '-vn'} #ffmpeg settings

class MusicBot(commands.Cog):
        def __init__(self, client):
            self.client = client
            self.queue = []

        @commands.command()
        async def play(self, ctx, *, search):
                try:
                    if ctx.author.voice:
                        voice_channel = ctx.author.voice.channel 
                    else: 
                        None
                    if not voice_channel:
                        return await ctx.send("Пользователь не находится в голосовом канале") #if u not in voice channel
                    if not ctx.voice_client:
                        await voice_channel.connect()
                except Exception as exc:
                     print(exc)

                async with ctx.typing(): #searching
                        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                            try:
                                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                                if 'entries'in info:
                                    info = info['entries'][0]
                                url = info['url']
                                title = info['title']
                                self.queue.append((url, title))
                                await ctx.send(f'Добавил в очередь твой трек: **{title}**') #bot saying this on server
                            except Exception as exc:
                                print(exc)
                if not ctx.voice_client.is_playing(): #play next track if create queue 
                    await self.play_next(ctx)
        async def play_next(self, ctx):
                try:
                    if self.queue: #empty tracklist
                        url, title = self.queue.pop(0)
                        source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
                        ctx.voice_client.play(source, after=lambda _:self.client.loop.create_task(self.play_next(ctx)))
                    elif not ctx.voice_client.is_playing():
                        await ctx.send('Ой, а очередь то пустая') 
                except Exception as exc:
                    print(exc)
        @commands.command()
        async def skip(self, ctx): #skip track
               if ctx.voice_client and ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    await ctx.send('Пропуск...')
client = commands.Bot(command_prefix='/', intents=intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start('')

asyncio.run(main())  