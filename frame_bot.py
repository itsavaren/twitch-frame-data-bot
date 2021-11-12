#! python3.9
from twitchio.ext import commands
import sys, json, time
from datetime import date
from dust_db import *
from dust_scrape import *


##################################################################################
#GOOGLE SHEETS CONNECTION
##################################################################################



##################################################################################
#ARGUMENT INGESTION, VARIABLE INITIALIZATION AND JOIN
##################################################################################

try:
    set_prefix = sys.argv[1]
except IndexError:
    print('no arguments, setting prefix to !')
    set_prefix = '!'


channel_names = ['avaren','sajam','akafishperson','letsdaze_','lastcody','redditto','romolla','leafretv','garmakilma','voidashe']

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
        if message.author.name == 'ryanhunter':
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
        if ctx.author.name == 'ryanhunter':
            await ctx.send('Madroctos: @RyanHunter !ryan how does it geel')

    # @commands.command()
    # async def fd(self, ctx: commands.Context, character, move=None, detail=None):
    #     if character == 'help':
    #         await ctx.send(f'Format: !fd [character(partial ok)] [move input or name] [specific stat OR "detail"(optional)] eg: !fd gio 2d, !fd axl 5k detail, !fd ky 6p recovery.  Try !fdreadme for a link to full documentation.')
    #     char = char_select(character)
    #     await ctx.send(get_move_data(char, move.lower(), detail))

    @commands.command()
    async def fd(self, ctx: commands.Context, *, full_message = None):
        await ctx.send(parse_move(full_message))

    @commands.command()
    async def fdupdate(self, ctx: commands.Context):
        if ctx.author.is_mod or ctx.author.name == 'avaren':
            await ctx.send('scraping.')
            scrape_data()
            await ctx.send('scraped.')

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
        if ctx.author.name in ['avaren','madroctos','voidashe']:
            await ctx.send("pokiW")
        



bot = Bot()
bot.run()
