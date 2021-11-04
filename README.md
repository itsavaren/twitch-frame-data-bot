# Frame Data Bot
Twitch chat bot to scrape dustloop to a local sqlite3 database, and then retrieve data from the database via user query.

Uses twitchio for bot functions and bs4 (Beautiful Soup) to scrape the web.

## Quick Start

* Download everything.
* Install python if needed from https://www.python.org/downloads/
* Install twitchio and bs4
* Go to www.twitchtokengenerator.com and connect to your bot account.  save client key in a file in the directory with the script called token.txt
* run the bot in the command line using the following format: py scriptname.py [command prefix] [any number of channels separated by spaces]
* example launch command: `py parity_bot.py ! avaren letsdaze_` will join the bot to twitch channel avaren and letsdaze_ with the command prefix !




## Functionality

Scrapes dustloop's frame data page once per update command, saves the data into a sqlite db file.  Responds to queries from users.

Also some other stuff related to ryan


# Commands

## Normal Chatter Commands

- **!fd [character] [move name or input] [stat or 'detail']** searches the character database for a move with the query term as a partial or full match to an input or move name.  Returns the startup, onhit, and onblock stats of the move.  Adding a stat will pull for that stat specifically (onhit, recovery, etc) or adding 'detail' will output the full data of the move.**
- **!troy** woof
- **!miso** also woof


## Moderator Commands

- **!fdupdate** deletes database files and re-scrapes the data.


## Other Functionality

Measures time between RyanHunter's first chat of the day and the first chatter to use the !ryan command.  Prints who won and how long it took.

!geel command is available only to ryan, so he may bully Madroctos.



# To Do:

Implement better handling of queries with multiple results.  Currently prints the first result found.

Refactor move data persistence for easier manipulation by custom query modifiers, eg. if someone wants to ask for the damage of a move !fd character move damage would return the standard stats + damage.  adding detailed would return the entire list of move data.

add common alternative names for moves and look for those if nothing else found, eg 'hair car', 'dp' etc.
