# Frame Data Bot
Twitch chat bot to scrape dustloop to a local sqlite3 database, and then retrieve data from the database via user query.

Uses twitchio for bot functions and bs4 (Beautiful Soup) to scrape the web.

If you want me to add my instance to your channel (user: whattheBOTdoin) just add me on discord and ask: Avaren#3379


## Functionality

Scrapes dustloop's frame data page once per update command, saves the data into a sqlite db file.  Responds to queries from users.

Also some other stuff related to ryan


# Commands

## Normal Chatter Commands

- **!fd [character] [move name or input] [stat or 'detail']** searches the character database for a move with the query term as a partial or full match to an input or move name.  Returns the startup, onhit, and onblock stats of the move.  Adding a stat will pull for that stat specifically (onhit, recovery, etc) or adding 'detail' will output the full data of the move.**

Note on !fd:  for level 1/2/3 of nago/goldlewis moves, append .1 .2 .3, or .br to the input(eg: 5h.2 for level 2 5h). For Ky dragon install moves, prepend di. to the input (eg: di.623s).

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
