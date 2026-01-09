import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
from gtts import gTTS

# بارکردنی زانیارییەکان
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# --- ڕێکخستنی میوزیک ---
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'cookies.txt'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

@bot.event
async def on_ready():
    print(f'✅ بۆتەکە ئامادەیە: {bot.user.name}')

# --- ١. بەخێرهاتنی دەنگی خۆکار ---
@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id: return
    if before.channel is None and after.channel is not None:
        try:
            vc = await after.channel.connect()
            tts = gTTS(text="Welcome to Dark Zone Store", lang='en')
            tts.save("welcome.mp3")
            vc.play(discord.FFmpegPCMAudio("welcome.mp3"))
            while vc.is_playing(): await asyncio.sleep(1)
            await vc.disconnect()
        except Exception as e:
            print(f"Error: {e}")

# --- ٢. فەرمانەکانی میوزیک و قسەکردن ---
@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice: return await ctx.send("❌ بڕۆ ناو ڤۆیس!")
    if not ctx.voice_client: await ctx.author.voice.channel.connect()
    info = ytdl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
    ctx.voice_client.play(discord.FFmpegPCMAudio(info['url'], **ffmpeg_options))
    await ctx.send(f'🎵 لێدەدرێت: **{info["title"]}**')

@bot.command()
async def say(ctx, *, text):
    if not ctx.author.voice: return
    if not ctx.voice_client: await ctx.author.voice.channel.connect()
    gTTS(text=text, lang='en').save("say.mp3")
    ctx.voice_client.play(discord.FFmpegPCMAudio("say.mp3"))

# --- ٣. فەرمانەکانی بەڕێوەبردن (Ban, Mute, Deafen) ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f'🚫 {member.mention} باند کرا.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == member_name:
            await ctx.guild.unban(user)
            await ctx.send(f'✅ {user.mention} ئان‌باند کرا.')
            return

@bot.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member):
    await member.edit(mute=True)
    await ctx.send(f'🔇 {member.mention} بێدەنگ کرا.')

@bot.command()
@commands.has_permissions(mute_members=True)
async def unmute(ctx, member: discord.Member):
    await member.edit(mute=False)
    await ctx.send(f'🔊 بێدەنگی لەسەر {member.mention} لادرا.')

@bot.command()
@commands.has_permissions(mute_members=True)
async def deafen(ctx, member: discord.Member):
    await member.edit(deafen=True)
    await ctx.send(f'🎧 {member.mention} کرا بە Deafen.')

@bot.command()
async def stop(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect()

bot.run(TOKEN)
