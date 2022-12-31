import discord
from discord.ext import commands
import os, time, datetime, asyncio
from discord.utils import get


TOKEN = '' #BOT TOKEN
prefix = '*' # Bot prefix
console_ch = #id console chat(need a plugin DiscordSRV)
bot_ch = # id main channel for bot (If needed)
builder_ch = #id builders chat for (If needed)
bat_path = '' # Path to bat file. If you want use command start and restart (for minecraft server)
role_sm = # role id server master (to use the start and restart commands)
role_helper =  # role id helper
print(bat_path)
def read_builder(): #text for new builder
    with open('C:/Users/TeamCIS/Desktop/TeamCISHelperBot/new_builder.txt', 'r', encoding='utf-8') as data:
        return data.read()

text_builder = read_builder()
intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.change_presence(status=discord.Status.online, activity=discord.Game("by Котик Воркотик#6990"))

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('test')

@bot.command(name='role')
@commands.has_role(role_helper)
async def print(ctx, *, text):
    channel = bot.get_channel(console_ch)
    nick, role = text.split()
    await channel.send(f'lp user {nick} parent add {role}')
    await ctx.reply("Выдал")

@bot.command(name='start')
@commands.has_role(role_sm)
async def st(ctx, *arg):
    try:
        await ctx.reply("Начинаю")
    except: ctx.reply("Нет прав")
    else: os.startfile(bat_path)

@bot.command(name='restart')
@commands.has_role(role_sm)
async def restart(ctx):
    channel = bot.get_channel(console_ch)
    await channel.send('say Перезагрузка через 3 минуты!')
    await channel.send('save-all')
    await ctx.reply('Процесс перезагрузки начался!')
    await asyncio.sleep(2 * 60)
    await channel.send('say Перезагрузка через 1 минуту!')
    await asyncio.sleep(60)
    await channel.send('say Перезагрузка!!!')
    await asyncio.sleep(5)
    await channel.send('stop')
    await asyncio.sleep(5 * 60)
    await os.startfile(bat_path)

@bot.command(name='accept', pass_context = True)
@commands.has_role(role_helper)
async def addrole(ctx,user : discord.Member, nick):
    #await ctx.send(f'{user.mention}, {nick}')
    role = discord.utils.get(user.guild.roles, id=802893377833795584)
    await user.remove_roles(role)
    role = discord.utils.get( user.guild.roles, id =901933301315551262)
    await user.add_roles(role)
    channel_c = bot.get_channel(console_ch)
    channel_b = bot.get_channel(builder_ch)
    await channel_c.send(f'lp user {nick} parent add junior')
    await channel_b.send(f'{user.mention} {text_builder}')
    await ctx.reply('Принял новичка')


bot.run(TOKEN)