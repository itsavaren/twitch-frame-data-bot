#! python3.9
from twitchio.ext import commands
import sys, json, time
from datetime import date

from googletrans import Translator, constants
from pprint import pprint

from dust_db import *
from dust_scrape import *
from definitions import *
from translate import translate


##################################################################################
#ARGUMENT INGESTION, VARIABLE INITIALIZATION AND JOIN
##################################################################################

try:
    set_prefix = sys.argv[1]
except IndexError:
    print('no arguments, setting prefix to !')
    set_prefix = '!'

channel_names = ['avaren','sajam','akafishperson','letsdaze_','lastcody','redditto','romolla','leafretv','garmakilma','voidashe','abusywizard']

if sys.argv[2:]:
    for arg in sys.argv[2:]:
        channel_names.append(arg)
else:
    print('no additional channels')


print(f'Joining twitch channels {", ".join(channel_names)} with {set_prefix} set as command prefix.')

with open('token.txt') as fp:
    auth_token = fp.read()

with open('ryan.json') as fp:
    ryan_data = json.load(fp)

fish_deaths = 0

##################################################################################
#BOT INITIALIZATION
##################################################################################

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=auth_token, prefix=set_prefix, initial_channels=channel_names)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        global start
        if message.echo:
            return
        if message.content.startswith(set_prefix):
            print(f'{message.author.name}: {message.content}')
        if message.author.name == 'ryanhunter' and message.channel.name == 'sajam':
            today = str(date.today())
            if today != ryan_data['date']:
                start = time.time()
        await self.handle_commands(message)


    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f'Hello {ctx.author.name}.')
        print(f'Hello {ctx.author.name}')

    @commands.command()
    async def troy(self, ctx: commands.Context):
        await ctx.send('OhMyDog')
        print('OhMyDog')

    @commands.command()
    async def miso(self, ctx: commands.Context):
        await ctx.send('Wowee')
        print('Wowee')

    @commands.command()
    async def ryan(self, ctx: commands.Context):
        global start, ryan_data
        if ctx.channel.name == 'sajam':
            if 'start' in globals():
                end = time.time()
                elapsed = end - start
                await ctx.send(f'{ctx.author.name} won the daily ryan challenge in {elapsed:0.3f} seconds.')
                print(f'{ctx.author.name} won the daily ryan challenge in {elapsed:0.3f} seconds.')
                ryan_data['date'] = str(date.today())
                with open('ryan.json', 'w') as fp:
                    json.dump(ryan_data, fp, indent = 4)
                del start

    @commands.command()
    async def geel(self, ctx: commands.Context):
        if ctx.author.name in ['ryanhunter','avaren']:
            await ctx.send('"Madroctos: @RyanHunter !ryan how does it geel"')

    @commands.command()
    async def fd(self, ctx: commands.Context, *, full_message = None):
        if 'update' in full_message and ctx.author.name != 'avaren':
            return
        if full_message.split()[0] == 'help':
            await ctx.send(f'Format: !fd [character(partial ok)] [move name or input(partial ok)] [specified stat or "detail" for full move stats.  eg: !fd gio 2d startup, !fd ky stun dipper')
            return
        await ctx.send(parse_move(full_message))

    @commands.command()
    async def bbfd(self, ctx: commands.Context, *, full_message = None):
        await ctx.send('BBFD command is deprecated.  Use !fd for any game.')

    @commands.command()
    async def fdupdate(self, ctx: commands.Context, *, full_message = None):
        if ctx.author.is_mod or ctx.author.name == 'avaren':
            if not full_message:
                game = 'ggst'
            else:
                game =  full_message.split()[0]
            await ctx.send(f'Scraping {game.upper()} data from dustloop to local database.')
            scrape_data(game)
            await ctx.send(f'{game.upper()} database refreshed.')

    @commands.command()
    async def bbfdupdate(self, ctx: commands.Context):
        await ctx.send('BBFDupdate command is deprecated.  Use !fdupdate: "!fdupdate bbcf"')


    @commands.command()
    async def fdreadme(self, ctx: commands.Context):
        if ctx.author.is_mod or ctx.author.name == 'avaren':
            await ctx.send('Visit https://github.com/itsavaren/strive-frame-data-bot for documentation.') 
        
    @commands.command()
    async def weird(self, ctx: commands.Context):
        if ctx.author.is_mod:
            await ctx.send("There's a good kind of weird, and a bad kind of weird. Stick to the good kind.")

    @commands.command()
    async def pokiw(self, ctx: commands.Context):
        if ctx.author.name in ['avaren','madroctos','voidashe','moopoke', 'sajam']:
            await ctx.send("pokiW")

    @commands.command()
    async def messagetest(self, ctx: commands.Context, *, full_message = None):
        await ctx.send(full_message)

    @commands.command()
    async def define(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name != 'sajam':
            await ctx.send(define_word(full_message))

    @commands.command()
    async def glossary(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name == 'akafishperson':
            await ctx.send(f"@{ctx.author.name}: https://glossary.infil.net/?t=" + full_message.replace(' ','+'))

    @commands.command()
    async def silksong(self, ctx: commands.Context):
        await ctx.send(f"Silksong is never coming out")
    
    @commands.command()
    async def translate(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name != 'sajam':
            await ctx.send(translate(full_message))

    @commands.command()
    async def fishsong(self, ctx: commands.Context):
        if ctx.channel.name == 'akafishperson':
            await ctx.send(f"✅ Verses don't rhyme  ✅ Wrong number of syllables  ✅ Performed with love  ✅ Must be an akaFishperson cover")




bot = Bot()
bot.run()
