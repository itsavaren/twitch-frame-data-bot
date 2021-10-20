#! python3.9
from twitchio.ext import commands
import sys
from framedatabase import *
from dustwikisearch import *


##################################################################################
#GOOGLE SHEETS CONNECTION
##################################################################################



##################################################################################
#ARGUMENT INGESTION, VARIABLE INITIALIZATION AND JOIN
##################################################################################

try:
    set_prefix = sys.argv[1]
except IndexError:
    print('incorrect arguments')


channel_names = []

if sys.argv[2:]:
    for arg in sys.argv[2:]:
        channel_names.append(arg)
else:
    print('incorrect arguments')


print(f'Joining twitch channels {", ".join(channel_names)} with {set_prefix} set as command prefix.')

with open('token.txt') as fp:
    auth_token = fp.read()

##################################################################################
#BOT INITIALIZATION
##################################################################################

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=auth_token, prefix=set_prefix, initial_channels=channel_names)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):

        if message.echo:
            return
        if message.content.startswith(set_prefix):
            print(f'{message.author.name}: {message.content}')
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
        await ctx.send('HypeTongue')
        print('HypeTongue')


    @commands.command()
    async def fd(self, ctx: commands.Context, character, move):
        if ctx.author.is_mod or ctx.author.name == 'avaren':
            raw = char_select(character)
            urlparsed = raw.title().replace(" ","_")
            sqlparsed = urlparsed.replace('-','_')
            await ctx.send(get_move_data(sqlparsed, move.upper()))

    @commands.command()
    async def fdupdate(self, ctx: commands.Context):
        if ctx.author.is_mod or ctx.author.name == 'avaren':
            await ctx.send('scraping.')
            full_scrape()
            await ctx.send('scraped.')
        




bot = Bot()
bot.run()
