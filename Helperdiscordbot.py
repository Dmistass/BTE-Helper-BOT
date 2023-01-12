import discord
from discord.ext import commands
import os, time, datetime, asyncio, json
from discord.utils import get
from pprint import pprint
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
from configparser import ConfigParser

#config
config_path = os.getcwd() + "/config.ini"
config = ConfigParser(inline_comment_prefixes = ('#', ';'))
config.read(config_path, encoding = "utf-8")
basic_cfg = config["BASIC"]
role_cfg = config["ROLES"]
channel_cfg = config["CHANNELS"]
restart_cfg = config["RESTART"]
texts_cfg = config["TEXTS"]

TOKEN = '' #BOT TOKEN
prefix = basic_cfg["prefix"] # Bot prefix
console_ch = int(channel_cfg["console"]) #id console chat(need a plugin DiscordSRV) to send console meddages through discord
bot_ch = int(channel_cfg["main"]) # main channel for bot (If needed)
builder_ch = int(channel_cfg["builders"])# 928941669049577472 builders chat (If needed)
helper_ch = int(channel_cfg["helpers"])
bat_path = basic_cfg["bat"] # If you want use command start and restart (for minecraft server)
role_sm = int(role_cfg["server_master"]) # role id server master (to use the start and restart commands)
role_helper = int(role_cfg["helper"]) # role id helper
head_helper = role_cfg["head_helper"]
sm_ch = int(channel_cfg["server_masters"])
papka_bota_path = os.getcwd() # 'C:/Users/TeamCIS/Desktop/TeamCISHelperBot/'
print(bat_path)
def read_builder(): #text for new builder
    with open(f"{papka_bota_path}" + '/new_builder.txt', 'r', encoding='utf-8') as data:
        return data.read()

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

manual_restart = 0

# restart time
frequency = int(restart_cfg["frequency"])
stop_h = int(restart_cfg["time"])//10000
stop_m = int(restart_cfg["time"])%10000//100
stop_s = int(restart_cfg["time"])%100

bot = commands.Bot(command_prefix=prefix, intents=intents)

async def read_helpers(id):
    with open(f"{papka_bota_path}" + "/Helpers.txt", 'r', encoding='utf-8') as data:
        for line in data:
            line = line.rstrip('\n')
            ID, nick = line.split('/')
            if int(ID) == id:
                return nick
            else: pass
    return

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Фыромяу')
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(name=f'by Котик Воркотик#6990', type=discord.ActivityType.playing))
    return

@bot.command(name='role')
@commands.has_role(role_helper)
async def print(ctx, *, text):
    channel = bot.get_channel(console_ch)
    nick, role = text.split()
    await channel.send(f'lp user {nick} parent add {role}')
    await ctx.reply("Выдал")
    return

@bot.command(name='start')
@commands.has_role(role_sm)
async def st(ctx, *arg):
    channel = bot.get_channel(console_ch)
    await channel.send('stop')
    ctx.reply(texts_cfg["start_msg"])
    await  asyncio.sleep(int(texts_cfg["start_delay"]) * 60)
    os.startfile(bat_path)
    return

async def restart(ctx):
    global manual_restart
    channel = bot.get_channel(console_ch)
    await channel.send(texts_cfg["full_rst_timer_msg"])
    await channel.send('save-all')
    await ctx.reply(texts_cfg["rst_reply"])
    await channel.send(texts_cfg["cmi_bossbar"])
    await asyncio.sleep(int(restart_cfg["full_rst_timer"]) - int(restart_cfg["small_rst_timer"]))
    await channel.send(restart_cfg["small_rst_timer_msg"])
    await asyncio.sleep(int(restart_cfg["small_rst_timer"]))
    await channel.send(texts_cfg["rst_msg"])
    await asyncio.sleep(5)
    await channel.send('stop')
    await asyncio.sleep(int(restart_cfg["stop_timer"]))
    os.startfile(bat_path)
    if manual_restart == 0:
        await restart_timer(ctx)
    return

@bot.command(name='restart')
@commands.has_role(role_sm)
async def manual_restart(ctx):
    global manual_restart
    manual_restart = 1
    await restart(ctx)
    return

@bot.command(name="autorestart",pass_context = True)
@commands.has_role(role_sm)
async def restart_timer(ctx):
    global manual_restart
    channel = bot.get_channel(sm_ch)
    start_h = time.strftime('%H')
    start_m = time.strftime('%M')
    start_s = time.strftime('%S')
    wait_time_h = (stop_h - start_h) * 60 * 60
    wait_time_m = (stop_m - start_m) * 60
    wait_time_s = (stop_s - start_s)
    if wait_time_h <= 0:
        wait_time_h = wait_time_h + ((frequency * 24) - 1) * 60 * 60
    if wait_time_m <= 0:
        wait_time_m = wait_time_m + 59 * 60
    if wait_time_s <= 0:
        wait_time_s = wait_time_s + 60
    wait_time = wait_time_h + wait_time_m + wait_time_s
    await channel.send(f"{wait_time}") #sends time left till restart
    await asyncio.sleep(wait_time)
    manual_restart = 0
    await restart(ctx)
    return

@bot.command(name='accept', pass_context = True)
@commands.has_role(role_helper)
async def addrole(ctx,user : discord.Member, nick):
    text_builder = read_builder()
    #await ctx.send(f'{user.mention}, {nick}')
    role = discord.utils.get(user.guild.roles, id = (int(role_cfg["beginner"])))
    await user.remove_roles(role)
    role = discord.utils.get( user.guild.roles, id = (int(role_cfg["junior"])))
    await user.add_roles(role)
    channel_con = bot.get_channel(console_ch)
    channel_buil = bot.get_channel(builder_ch)
    channel_help = bot.get_channel(helper_ch)
    await channel_con.send(f'lp user {nick} parent add junior')
    await channel_buil.send(f'{user.mention} {text_builder}')
    await ctx.reply('Принял новичка')
    await channel_help.send(f'{head_helper} {user.mention} {texts_cfg["hh_not"]}')
    return

@bot.command(name='mult')
@commands.has_role(role_helper)
async def mult(ctx, user : discord.Member):
    with open(f"{papka_bota_path}" + "/mult.txt", 'r', encoding='utf-8') as data:
        text = data.read()
    await ctx.send(f'{user.mention} привет! \n\n{text}')
    await ctx.message.delete()
    return

@bot.command(name='singl')
@commands.has_role(role_helper)
async def mult(ctx, user : discord.Member):
    with open(f"{papka_bota_path}" + "/singl.txt", 'r', encoding='utf-8') as data:
        text = data.read()
    await ctx.send(f'{user.mention} привет! \n\n{text}')
    await ctx.message.delete()
    return

@bot.command(name='mult18')
@commands.has_role(role_helper)
async def mult(ctx, user : discord.Member):
    with open(f"{papka_bota_path}" + "/mult18.txt", 'r', encoding='utf-8') as data:
        text = data.read()
    await ctx.send(f'{user.mention} привет! \n\n{text}')
    await ctx.message.delete()
    return

@bot.command(name='apply')
@commands.has_role(role_helper)
async def mult(ctx):
    with open(f"{papka_bota_path}" + "/apply.txt", 'r', encoding='utf-8') as data:
        text = data.read()
    await ctx.send(f'{text}')
    await ctx.message.delete()
    return

@bot.command(name='task')
@commands.has_role(role_helper)
async def task(ctx, user : discord.Member, nick):
    CRED = 'C:/Users/dmist/Desktop/TeamCISHelperBot/CRED.json' #i don't want to touch this mess even if it's not actual mess
    spreadsheet_id = '1Bp0SvkDhgZ9w4pLxiN5cnKiMuK46U3-YKrZ2dnMdB-I'
    helper = read_helpers(ctx.author.id)

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    servise = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    values = servise.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='B5:B5',
                                                 majorDimension='ROWS').execute()
    #text_task = json.loads(str(values))
    await ctx.send(f'{user.mention}\n\n{str(values["values"][0][0])}')

    values = servise.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                         body={
                                                             "valueInputOption": "USER_ENTERED",
                                                             "data": [{"range": "B6:B7",
                                                                       "majorDimension": "COLUMNS",
                                                                       "values": [
                                                                           [f"{user}", f"{nick}"]]},
                                                                      {"range": "C7:C7",
                                                                       "majorDimension": "COLUMNS",
                                                                       "values": [
                                                                           [f"{helper}"]]},
                                                                      {"range": "B18:B18",
                                                                       "majorDimension": "COLUMNS",
                                                                       "values": [
                                                                           ["TRUE"]]}
                                                                      ]
                                                         }).execute()
    return

bot.run(TOKEN)