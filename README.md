*Soon to be updated.*

# Frame Data Bot
Twitch chat bot to scrape dustloop to a local sqlite3 database, and then retrieve data from the database via user query.

Uses twitchio for bot functions and bs4 (Beautiful Soup) to scrape the web.



# Commands

## Normal Chatter Commands

- **!fd [game(optional)] [character] [move name or input] [stat or 'detail'(optional)]** searches the character database for a move with the query term as a partial or full match to an input or move name.  Returns the startup, onhit, and onblock stats of the move.  Adding a stat will pull for that stat specifically (onhit, recovery, etc) or adding 'detail' will output the full data of the move.**

Note on !fd:  for level 1/2/3 of nago/goldlewis moves, append .1 .2 .3, or .br to the input(eg: 5h.2 for level 2 5h). For Ky dragon install moves, prepend di. to the input (eg: di.623s).

- **!fd help** for format help and examples.
- **!fdreadme** to get a link to this readme page.

- **!troy** woof
- **!miso** also woof
- **!pokiw** PokiW if you are the broadcaster or on a shortlist of VIPs. (only works if the bot is subbed to pokimane)
- **!songid** Captures 10 seconds of stream audio and checks against a content match library for known songs via https://audd.io/
- **!define [word]** Returns definition for submitted word via https://dictionaryapi.dev/
- **!translate [2 character language code][word]** Returns translation of word given into the language specified (french if not specified).  !translate ? [language] to retrieve the 2 letter code.
- **!rank or !lp [username]** Checks http://na.op.gg/ for username's ranked league and LP.


## Moderator Commands

- **!fdupdate [4 character game abbreviation]** deletes database files and re-scrapes the data for that game. defaults to guilty gear strive.  games supported: guilty gear strive(ggst), blazblue centralfiction(bbcf), persona 4 arena ultimax(p4u2), dungeon fighter: duel(dnfd).


## Other Functionality
- Measures time between RyanHunter's first chat of the day and the first chatter to use the !ryan command.  Prints who won and how long it took.



# Activation/Installation

## Join my instance to your channel

If you want me to add my instance to your channel (user: whattheBOTdoin) just add me on discord and ask: Avaren#3379

## Installation instructions

* Download all files.
* Create chat user token at https://twitchtokengenerator.com/
* For song ID functionality, create an api user account at https://dashboard.audd.io/
* Put token into a file named token.txt in the same directory as the files.  optionally put your audd.io token in a file called audd_token.txt in the same directory.
* Edit channel_names variable in frame_bot.py to your channel name only.  Remove section below it marked for deletion incase of running your own instance.
* On the device you will run the bot, install python 3.9.x
* From the command line in the directory with the bot files, run pip install -r requirements.txt
* From the command line in the directory with the bot files, run python frame_boy.py

# To Do:

add common alternative names for moves and look for those if nothing else found, eg 'hair car', 'dp' etc.
