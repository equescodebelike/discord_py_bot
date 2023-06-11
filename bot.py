import discord
from discord.ext import commands
import datetime, pyowm
from discord.utils import get
import youtube_dl
import os
import random

TOKEN = 'INSERT YOUR TOKEN THERE'

client = commands.Bot(command_prefix = '!')
bot = commands.Bot(command_prefix='!')
que = []
bot.remove_command('help')

@bot.event
async def on_ready():
	print('Datum Bot Beta запущен!')

@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def say(ctx, *, arg):  # создаем асинхронную фунцию бота
    await ctx.send(arg)  # отправляем обратно аргумент

@bot.command()
async def hi(ctx):
    msg = await ctx.send("Привет, {} :sunglasses:".format(ctx.message.author.mention))

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Datum Bot", description="Datum Bot Beta версия", color=0xeee657)

    embed.add_field(name="Разработчик", value="arkhip") 
    embed.add_field(name="Количество серверов", value=f"{len(bot.guilds)}") 
    embed.add_field(name="Добавить бота на свой сервер", value="https://discordapp.com/oauth2/authorize?client_id=627797231843540992&scope=bot")
    embed.add_field(name="Дополнительно", value="Список команд: !commands")
    await ctx.send(embed=embed)

@bot.command()
async def commands(ctx):
    embed = discord.Embed(title="Datum Bot список команд:", color=0xeee657)

    embed.add_field(name="!joined [@пользователь]", value="Дата присоединения к серверу пользователя", inline=False)
    embed.add_field(name="!hi", value="Поприветствовать бота", inline=False)
    embed.add_field(name="!say", value="Написать любое сообщение от лица бота (!say текст)", inline=False)
    embed.add_field(name="!roll [число]", value="Случайное число в диапазоне от 0 до заданного", inline=False)
    embed.add_field(name="!randomslap", value="Упомянуть случайного пользователя", inline=False)
    embed.add_field(name="!info", value="Информация о боте", inline=False)
    embed.add_field(name="!play [url] !join !leave", value="Запустить видео с ютуба", inline=False)
    embed.add_field(name="!avatar [@пользователь]", value="Аватар пользователя", inline=False)
    embed.add_field(name="!coin", value="Монетка", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send('{0} присоединился к серверу {0.joined_at}'.format(member))

@bot.command(pass_context=True)
async def roll(ctx, number):
    try:
        arg = random.randint(1, int(number))
    except ValueError:
        await ctx.send("Неверное число")
    else:
        await ctx.send("Случайное число в заданном диапазоне: " +str(arg))

@bot.command()
async def coin( ctx ):
    coins = [ 'орел', 'решка' ]
    coins_r = random.choice( coins )
    coin_win = 'орел'

    if coins_r == coin_win:
        await ctx.send(embed = discord.Embed(description= f''':tada: { ctx.message.author.name }, выиграл! 
            Тебе повезло у тебя: ``{ coins_r }``''', color = 0x0c0c0c))

    if coins_r != coin_win:
        await ctx.send(embed = discord.Embed(description= f''':thumbsdown:  { ctx.message.author.name }, проиграл! 
            Тебе не повезло у тебя: ``{ coins_r }``''', color = 0x0c0c0c)) 

@bot.command()
async def avatar(ctx, member : discord.Member = None):
    user = ctx.message.author if (member == None) else member
    embed = discord.Embed(title=f'Аватар пользователя {user}', color= 0x0c0c0c)
    embed.set_image(url=user.avatar_url)
    await ctx.send(embed=embed)

@bot.command()
async def randomslap(ctx):
     to_slap = random.choice(ctx.guild.members)
     await ctx.send('{0.author} шлепнул {1}'.format(ctx, to_slap))

@bot.command()
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

@bot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()

@bot.command()
async def play(ctx, url : str):
    song_there = os.path.isfile('song.mp3')

    try:
        if song_there:
            os.remove('song.mp3')
            print('[log] Старый файл удален')
    except PermissionError:
        print('[log] Не удалось удалить файл')

    await ctx.send('Загрузка...')

    voice = get(bot.voice_clients, guild = ctx.guild)

    ydl_opts = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192'
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('[log] Загружаю музыку...')
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            print(f'[log] Переименовываю файл: {file}')
            os.rename(file, 'song.mp3')

    voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, музыка закончила свое проигрывание'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.1

    song_name = name.rsplit('-', 2)
    await ctx.send(f'Сейчас играет: {song_name[0]}')


@bot.command()
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Воспроизведение приостановлено")
        voice.pause()
        await ctx.send("Воспроизведение приостановлено")
    else:
        print("Нет воспроизводимой музыки")
        await ctx.send("Нет воспроизводимой музыки")


@bot.command()
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        print("Музыка возобновлена")
        voice.resume()
        await ctx.send("Продолжаем!")
    else:
        print("Музыка не приостановлена")
        await ctx.send("Музыка не приостановлена")


@bot.command()
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Музыка остановлена")
        voice.stop()
        await ctx.send("Музыка остановлена")
    else:
        print("Нет воспроизводимой музыки")
        await ctx.send("Нет воспроизводимой музыки")


@bot.command()
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send("Не подключен к голосовому каналу")
    print(volume/100)
    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Громкость изменена на {volume}%")


@bot.command() 
async def ban(ctx,member: discord.Member = None, reason = None): 

    if member is None:
        await ctx.send(embed = discord.Embed(description = '**:grey_exclamation: Обязательно укажите: пользователя!**'))
    elif reason is None:
        await ctx.send(embed = discord.Embed(description = '**:grey_exclamation: Обязательно укажите: причину!**'))
    else:    
        channel_log = bot.get_channel(670260939249156096) #Айди канала логов

        await member.ban( reason = reason )
        await ctx.send(embed = discord.Embed(description = f'**:shield: Пользователь {member.mention} был заблокирован.\n:book: По причине: {reason}**', color=0x0c0c0c)) 
        await channel_log.send(embed = discord.Embed(description = f'**:shield: Пользователь {member.mention} был заблокирован.\n:book: По причине: {reason}**', color=0x0c0c0c))

@bot.command()
async def weather( ctx, *, arg ):
    owm = pyowm.OWM( 'API' ) # https://openweathermap.org/api_keys
    city = arg

    observation = owm.weather_at_place( city )
    weather = observation.get_weather()
    temperature = w.get_temperature( 'celsius' )[ 'temp' ]

    await ctx.send( f'Температура в { city } : { temperature }' )

        
bot.run(TOKEN)