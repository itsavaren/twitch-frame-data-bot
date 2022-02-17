#! python3.9
from twitchio.ext import commands
import sys, json, time
from datetime import date
from dust_db import *
from dust_scrape import *
from definitions import *
from translate import translate
from rankfinder import *
from songid import *
from bingus import *
from wiki_lookup import *
from dggg import *
# from twitchio.ext.commands import core
# from googletrans import Translator, constants
# from pprint import pprint


##################################################################################
#ARGUMENT INGESTION, VARIABLE INITIALIZATION AND JOIN
##################################################################################


#set prefix to first command line argument, or default to !
try:
    set_prefix = sys.argv[1]
except IndexError:
    print('no arguments, setting prefix to !')
    set_prefix = '!'

#list of channels to join
channel_names = ['avaren','sajam','akafishperson','letsdaze_','lastcody',
'redditto','romolla','leafretv','garmakilma','voidashe','abusywizard','moopoke','deyvonnn','hotashi','mrmouton','kizziekay310','destiny','notsoerudite','diaphone_']


fighter_channels = channel_names
simple_meme_channels = channel_names
complex_meme_channels = channel_names
glossary_channels = channel_names
league_channels = channel_names
songid_channels = channel_names


##########
#DELETE BELOW IF YOU RUN YOUR OWN INSTANCE
##########
fighter_channels = ['avaren','sajam','akafishperson','letsdaze_','lastcody',
'redditto','romolla','leafretv','garmakilma','voidashe','abusywizard','moopoke','deyvonnn','hotashi','kizziekay310','diaphone_']

simple_meme_channels = ['avaren','sajam','akafishperson','letsdaze_','lastcody',
'redditto','romolla','leafretv','garmakilma','voidashe','abusywizard','moopoke','deyvonnn','hotashi','mrmouton']

complex_meme_channels = ['avaren','akafishperson','letsdaze_','lastcody',
'redditto','leafretv','garmakilma','voidashe','abusywizard','moopoke','deyvonnn','mrmouton']

glossary_channels = ['avaren','akafishperson','letsdaze_','lastcody',
'leafretv','voidashe','abusywizard','deyvonnn',]

league_channels = ['avaren','mrmouton','destiny']

songid_channels = ['avaren','mrmouton','voidashe','akafishperson','hotashi','leafretv']

wiki_channels = ['avaren','akafishperson', 'notsoerudite','mrmouton']
##########
#DELETE ABOVE IF YOU RUN YOUR OWN INSTANCE
##########

#check for command line arguments after prefix argument for additional channels to join
if sys.argv[2:]:
    for arg in sys.argv[2:]:
        channel_names.append(arg)
else:
    print('no additional channels')

print(f'Joining twitch channels {", ".join(channel_names)} with {set_prefix} set as command prefix.')

#open twitch user api token file
with open('token.txt') as fp:
    auth_token = fp.read()

#open daily ryan contest data file
try:
    with open('./db/ryan.json') as fp:
        ryan_data = json.load(fp)
except:
    ryan_data = {}
    with open('./db/ryan.json', 'w') as fp:
        json.dump(ryan_data, fp, indent = 4)


##################################################################################
#BOT INITIALIZATION
##################################################################################

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=auth_token, prefix=set_prefix, initial_channels=channel_names, case_insensitive = True)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    #ignore incorrect command errors
    async def event_command_error(self, context: commands.Context, error: Exception):
        pass

    async def event_message(self, message):
        #make start a global variable if it isn't already, for ryan stuff. this is bad, I know.  the whole ryan thing needs a re-think but it works for now
        global start
        #ignore own messages
        if message.echo:
            print(f'{message.channel} {message.content}')
            return
        #print chatter's successful command uses
        # if message.content.startswith(set_prefix):
        #     print(f'[{message.channel}]{message.author.name}: {message.content}')
        #more ryan stuff
        if message.author.name == 'ryanhunter' and message.channel.name == 'sajam':
            today = str(date.today())
            if today != ryan_data['date']:
                start = time.time()
        await self.handle_commands(message)


#commands start
    @commands.command()
    async def hello(self, ctx: commands.Context):
        if ctx.author.is_mod or ctx.author.name == 'avaren':
            await ctx.send(f'Hello {ctx.author.name} in {ctx.channel.name}.  I am alive. MrDestructoid')

    @commands.command()
    async def troy(self, ctx: commands.Context):
        await ctx.send('OhMyDog')

    @commands.command()
    async def miso(self, ctx: commands.Context):
        await ctx.send('Wowee')

    @commands.command()
    async def ryan(self, ctx: commands.Context):
        global start, ryan_data
        if ctx.channel.name == 'sajam':
            if 'start' in globals():
                end = time.time()
                elapsed = end - start
                elapsed = round(elapsed,5)
                try: 
                    ryan_data['winners'][ctx.author.name]
                except KeyError:
                    ryan_data['winners'][ctx.author.name] = 0
                await ctx.send(f"{ctx.author.name} won the daily ryan challenge in {elapsed} seconds. Wins: {ryan_data['winners'][ctx.author.name]+1}")
                ryan_data['date'] = str(date.today())
                ryan_data['winners'][ctx.author.name] += 1
                if elapsed < ryan_data['record_time']:
                    ryan_data['record_time'] = elapsed
                    ryan_data['record_holder'] = ctx.author.name
                    await ctx.send(f'A new record!  Congratulations {ctx.author.name}.')
                with open('./db/ryan.json', 'w') as fp:
                    json.dump(ryan_data, fp, indent = 4)
                del start

    @commands.command()
    async def ryanstats(self, ctx: commands.Context, *, full_message = None):
        global ryan_data
        if ctx.channel.name == 'sajam':
            if full_message and full_message.split()[0] == 'record':
                await ctx.send(f"The current record holder is {ryan_data['record_holder']} with a time of {ryan_data['record_time']} seconds.")
            else:
                try: 
                    ryan_data['winners'][ctx.author.name]
                except KeyError:
                    return
                await ctx.send(f"@{ctx.author.name} You have won the Ryan challenge {ryan_data['winners'][ctx.author.name]} times.")

    @commands.command()
    async def fd(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in fighter_channels:
            #prevent anyone but me from updating database notes from chat
            if 'update' in full_message and ctx.author.name != 'avaren':
                return
            #handle !fd help requests, common guess for help with the bot
            if full_message.split()[0] == 'help':
                await ctx.send(f'Format: !fd [character(partial ok)] [move name or input(partial ok)] [specified stat or "detail" for full move stats.  eg: !fd gio 2d startup, !fd ky stun dipper')
                return
            await ctx.send(parse_move(full_message))

    @commands.command()
    async def fdupdate(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in fighter_channels:
            #only allows streamer or me to scrape new data
            if ctx.author.name == ctx.channel.name or ctx.author.name == 'avaren':
                #if no argument, scrape guilty gear strive
                if not full_message:
                    game = 'ggst'
                else:
                    game =  full_message.split()[0]
                await ctx.send(f'Scraping {game.upper()} data from the web to local database.')
                scrape_data(game)
                await ctx.send(f'{game.upper()} database refreshed.')

    @commands.command()
    async def fdreadme(self, ctx: commands.Context):
        if ctx.channel.name in fighter_channels:
            if ctx.author.is_mod or ctx.author.name == 'avaren':
                await ctx.send('Visit https://github.com/itsavaren/strive-frame-data-bot for documentation.') 

    @commands.command()
    async def pokiw(self, ctx: commands.Context):
        if ctx.author.name in ['avaren','madroctos','voidashe','moopoke', 'sajam', 'flaskpotato','kierke'] or ctx.author.name == ctx.channel.name:
            await ctx.send("pokiW")

    @commands.command()
    async def define(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in complex_meme_channels:
            await ctx.send(define_word(full_message))

    @commands.command()
    async def glossary(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in glossary_channels:
            await ctx.send(f"@{ctx.author.name}: https://glossary.infil.net/?t=" + full_message.replace(' ','+'))

    @commands.command()
    async def silksong(self, ctx: commands.Context):
        if ctx.channel.name in simple_meme_channels:
            await ctx.send(f"Silksong is never coming out")
    
    @commands.command()
    async def translate(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in complex_meme_channels:
            await ctx.send(translate(full_message))

    @commands.command()
    async def fishsong(self, ctx: commands.Context):
        if ctx.channel.name == 'akafishperson':
            await ctx.send(f"✅ Verses don't rhyme  ✅ Wrong number of syllables  ✅ Performed with love  ✅ Must be an akaFishperson cover")

    @commands.command()
    async def rank(self, ctx: commands.Context, *, full_message = None): 
        if ctx.channel.name in league_channels:
            if not full_message:
                if ctx.channel.name == 'mrmouton':
                    full_message = 'iammentallyill'
                if ctx.channel.name == 'destiny':
                    full_message = 'yorha destiny'
            await ctx.send(f'@{ctx.author.name} {get_rank(full_message)}')
        
    @commands.command()
    async def lp(self, ctx: commands.Context, *, full_message = None): 
        if ctx.channel.name in league_channels:
            if not full_message:
                if ctx.channel.name == 'mrmouton':
                    full_message = 'iammentallyill'
                if ctx.channel.name == 'destiny':
                    full_message = 'yorha destiny'
            await ctx.send(f'@{ctx.author.name} {get_rank(full_message)}')

    @commands.command()
    async def songid(self, ctx: commands.Context):
        if ctx.channel.name in songid_channels:
            await ctx.send(f'@{ctx.author.name} {identify_song(ctx.channel.name)}')

    @commands.command()
    async def orcs(self, ctx: commands.Context):
        if ctx.channel.name in simple_meme_channels:
            await ctx.send(f'SMOrc SMOrc SMOrc')

    @commands.command()
    async def bingus(self, ctx: commands.Context):
        if ctx.channel.name in simple_meme_channels:
            await ctx.send(f'The current price of bingus is ${bingus_quote()}')

    @commands.command()
    async def wiki(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in wiki_channels:
            await ctx.send(wiki_def(full_message)[0:490])

    @commands.command()
    async def dg(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in league_channels:
            if 'blood' in full_message:
                await ctx.send(first_winrate('blood'))
            if 'dragon' in full_message or 'drake' in full_message:
                await ctx.send(first_winrate('drake'))
            else:
                await ctx.send(champ_winrate(select_champ(full_message)))

    @commands.command()
    async def dgload(self, ctx: commands.Context, *, full_message = None):
        if ctx.channel.name in league_channels and ctx.author.name in ['avaren','kierke']:
            await ctx.send('Attempting to get fresh matches.')
            load_history(full_message)

    @commands.command()
    async def dgtotal(self, ctx: commands.Context):
        if ctx.channel.name in league_channels:
            await ctx.send(f'Database contains{total_matches()} matches.')


bot = Bot()
bot.run()
