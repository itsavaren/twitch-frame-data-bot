import requests, json, re, ujson
import cassiopeia as cass
import sqlite3, time

requests.models.complexjson = ujson



def connect():
    """Connect to the database and create the table if necessary."""
    #open the database file
    conn =sqlite3.connect(f'./db/match_history.db')
    #create cursor
    cur = conn.cursor()
    #create the table if it isn't in there
    cur.execute('''CREATE TABLE IF NOT EXISTS matches(match_id TEXT PRIMARY KEY, duration INTEGER, player TEXT, first_drake INTEGER, first_blood INTEGER, win INTEGER,
     moot_champ TEXT DEFAULT NULL, dest_champ TEXT DEFAULT NULL, offrole TEXT, ally_top TEXT, ally_jung TEXT, ally_mid TEXT,
      ally_bot TEXT, ally_sup TEXT, enemy_top TEXT, enemy_jung TEXT, enemy_mid TEXT, enemy_bot TEXT, enemy_sup TEXT)''')
    #commit any changes
    conn.commit()
    #close the connection
    conn.close()

def total_matches():
    """Get total number of matches in database."""
    conn =sqlite3.connect(f'./db/match_history.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM matches")
    total_matches = cur.fetchall()[0][0]
    conn.close()
    return total_matches

def solo_duo_winrate():
    """Get the winrates of a champion."""
    conn =sqlite3.connect(f'./db/match_history.db')
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM matches")
    total_games = cur.fetchall()[0][0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE player = ?",('moot',))
    total_moot_games = cur.fetchall()[0][0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE win=1 AND player = ?",('moot',))    
    won_moot_games = cur.fetchall()[0][0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE player = ?",('dest',))
    total_dest_games = cur.fetchall()[0][0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE win=1 AND player = ?",('dest',))    
    won_dest_games = cur.fetchall()[0][0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE player = ?",('duo',))
    total_duo_games = cur.fetchall()[0][0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE win=1 AND player = ?",('duo',))    
    won_duo_games = cur.fetchall()[0][0]
    moot_winrate = (won_moot_games / total_moot_games) * 100
    dest_winrate = (won_dest_games / total_dest_games) * 100
    duo_winrate = (won_duo_games / total_duo_games) * 100

    return f'Winrates({total_games} games): Moot = {moot_winrate:.2f}%, Steve = {dest_winrate:.2f}%, Duo: {duo_winrate:.2f}%'

def champ_winrate(champion, mode = None):
    """Get the winrates of a champion."""
    if not champion:
        return "Champion not found."

    conn =sqlite3.connect(f'./db/match_history.db')
    cur = conn.cursor()

    #get total rows where champion is an ally
    cur.execute("SELECT COUNT(*) FROM matches WHERE ? IN (ally_bot, ally_jung, ally_mid, ally_sup, ally_top) AND ? NOT IN (dest_champ, moot_champ)",(champion, champion))
    total_ally_games = cur.fetchall()[0][0]
    #get total rows where champion is an ally and player won
    cur.execute("SELECT COUNT(*) FROM matches WHERE win=1 AND ? IN (ally_bot, ally_jung, ally_mid, ally_sup, ally_top) AND ? NOT IN (dest_champ, moot_champ)",(champion, champion))
    won_ally_games = cur.fetchall()[0][0]
    ally_winrate = (won_ally_games / total_ally_games) * 100

    #get total rows where champion is an enemy
    cur.execute("SELECT COUNT(*) FROM matches WHERE ? IN (enemy_bot, enemy_jung, enemy_mid, enemy_sup, enemy_top) AND ? NOT IN (dest_champ, moot_champ)",(champion, champion))
    total_enemy_games = cur.fetchall()[0][0]
    #get total rows where champion is an enemy and player won
    cur.execute("SELECT COUNT(*) FROM matches WHERE win=0 AND ? IN (enemy_bot, enemy_jung, enemy_mid, enemy_sup, enemy_top) AND ? NOT IN (dest_champ, moot_champ)",(champion, champion))
    won_enemy_games = cur.fetchall()[0][0]
    enemy_winrate = (won_enemy_games / total_enemy_games) * 100

    conn.close()
    if not mode:
        return f"{champion} has a {ally_winrate:.2f}% winrate as an ally(in {total_ally_games} games), and {enemy_winrate:.2f}% winrate as an enemy(in {total_enemy_games} games)."
    if mode == 'ally':
        return ally_winrate
    elif mode == 'enemy':
        return enemy_winrate


def first_winrate(stat):
    """Get the winrates of first blood/drake."""
    conn =sqlite3.connect(f'./db/match_history.db')
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM matches WHERE first_{stat} = 1")
    total_games = cur.fetchall()[0][0]
    cur.execute(f"SELECT COUNT(*) FROM matches WHERE win=1 and first_{stat} = 1")
    wins = cur.fetchall()[0][0]
    winrate = (wins / total_games) * 100
    return f"Getting first {stat} has a {winrate:.2f}% winrate(in {total_games} games)."

def duration_winrate(duration):
    """Get the winrate of games this long."""
    conn =sqlite3.connect(f'./db/match_history.db')
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM matches WHERE duration > ?",(duration,))
    total_games = cur.fetchall()[0][0]
    cur.execute(f"SELECT COUNT(*) FROM matches WHERE duration > ?AND win=1",(duration,))
    wins = cur.fetchall()[0][0]
    winrate = (wins / total_games) * 100
    
    return f"{winrate:.2f}% in {total_games} matches"

def offrole_winrate(streamer):
    """Get the winrate of games this long."""
    player = 'dest' if streamer == 'destiny' else 'moot'
    conn =sqlite3.connect(f'./db/match_history.db')
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM matches WHERE offrole=?",(player,))
    total_games = cur.fetchall()[0][0]
    cur.execute(f"SELECT COUNT(*) FROM matches WHERE offrole=? AND win=1",(player,))
    wins = cur.fetchall()[0][0]
    winrate = (wins / total_games) * 100
    
    return f"{streamer} offrole winrate: {winrate:.2f}% in {total_games} matches"



def insert_data(matches: list):
    """Insert matches into a sqlite database file."""
    conn =sqlite3.connect(f'./db/match_history.db')
    cur = conn.cursor()
    #create a string of comma separated question marks equal to the number of column names provided, to be used below
    val_count = ('?,'*len(matches[0]))[:-1]
    #insert the rows to the database table
    for move in matches:
        try:
            cur.execute('INSERT INTO matches VALUES (%s)' % val_count, (move))
            print(f'inserted {move[0]}')
        except Exception as e:
            print(e)
    conn.commit()
    conn.close()

def load_history(count=None):
    """Pull the match history from the API."""
    if not count:
        match_limit = 40
    elif count == 'full':
        match_limit = 10000
    else:
        match_limit = int(count)


    with open('riot_token.txt') as fp:
        riot_token = fp.read()


    steven = cass.Summoner(name='YoRHa Destiny', region='NA')
    lucas = cass.Summoner(name='IAmMentallyIll', region='NA')

    default_settings = cass.get_default_config()
    default_settings['global']['default_region'] = 'NA'
    default_settings['global']['version_from_match'] = 'version'
    cass.apply_settings(default_settings)
    cass.set_riot_api_key(riot_token)

    history_targets = [steven, lucas]


    for guy in history_targets:
        empties = 0
        begin_index = 0
        end_index = 21
        match_count = 0
        while True:
            try:
                print('scanning')

                mrm_history = cass.get_match_history(begin_index=begin_index, end_index=end_index, region=cass.data.Region.north_america,
                                                        queue=cass.data.Queue.ranked_solo_fives, puuid=guy.puuid,
                                                        continent=cass.data.Continent.americas)

                

                matches = []

                for match in mrm_history:
                    try:
                        match_id = match.id if type(match.id) == str else ('na1_'+str(match.id))
                        conn =sqlite3.connect(f'./db/match_history.db')
                        cur = conn.cursor()
                        cur.execute(f"SELECT COUNT(*) FROM matches WHERE match_id = ?",(match_id.lower(),))
                        id_check = cur.fetchall()[0][0]
                        if id_check:
                            #print(f'{match_id} found, skipping')
                            continue
                        match_seconds = int((match.duration * 1000).total_seconds())
                        if match.patch.major < '11':
                            print('patch too old, breaking')
                            break

                        ally_team_dict = {}
                        enemy_team_dict = {}
                        dest_champ = ''
                        moot_champ = ''
                        offrole = ''

                        if lucas in match.participants:
                            player = 'moot'
                            moot_part = match.participants[lucas]
                            moot_champ = moot_part.champion.name
                            
                            ally_team_dict['moot_champ'] = moot_champ
                            ally_team_dict['win'] = 1 if moot_part.stats.win else 0
                            ally_team = match.red_team if lucas in match.red_team else match.blue_team
                            if moot_part.team_position.name != 'utility':
                                ally_team_dict['offrole'] = 'moot'

                        if steven in match.participants:
                            player = 'dest'
                            dest_part = match.participants[steven]
                            dest_champ = dest_part.champion.name
                            
                            ally_team_dict['dest_champ'] = dest_champ
                            ally_team_dict['win'] = 1 if dest_part.stats.win else 0
                            ally_team = match.red_team if steven in match.red_team else match.blue_team
                            if dest_part.team_position.name != 'bot_lane':
                                ally_team_dict['offrole'] = 'dest'

                        ally_team_dict['first_drake'] = 1 if ally_team.first_dragon else 0
                        ally_team_dict['first_blood'] = 1 if ally_team.first_blood else 0

                        if lucas in match.participants and steven in match.participants:
                            player = 'duo'
                            if moot_part.team_position.name != 'bot_lane' and moot_part.team_position.name != 'utility':
                                ally_team_dict['offrole'] = 'both'
                            
                        for team in match.teams:
                            if lucas not in team and steven not in team:
                                enemy_team = team


                        for part in ally_team.participants:
                            ally_team_dict[part.team_position.name] = {}
                            ally_team_dict[part.team_position.name] = part.champion.name

                        for part in enemy_team.participants:
                            enemy_team_dict[part.team_position.name] = {}
                            enemy_team_dict[part.team_position.name] = part.champion.name

                        sql_list = [match_id, match_seconds, player, ally_team_dict['first_drake'], ally_team_dict['first_blood'], ally_team_dict['win'], moot_champ, dest_champ, offrole,
                        ally_team_dict['top_lane'], ally_team_dict['jungle'], ally_team_dict['mid_lane'], ally_team_dict['bot_lane'], ally_team_dict['utility'],
                        enemy_team_dict['top_lane'], enemy_team_dict['jungle'], enemy_team_dict['mid_lane'], enemy_team_dict['bot_lane'], enemy_team_dict['utility']]

                        new_sql_list = []

                        for entry in sql_list:
                            if type(entry) is str:
                                new_sql_list.append(entry.lower())
                            else:
                                new_sql_list.append(entry)
                        matches.append(new_sql_list)
                    except Exception as e:
                        print(f"error: {e} in match {match_id}")    
            except Exception as e:
                print(f"error: {e} in match {match_id}")

            print(f'length is {str(len(matches))}')
            print(f"inserting {guy.name}'s games")


            connect()
            try:
                insert_data(matches)
            except Exception as e:
                print(f'insertion error: {e}')
            begin_index += 20
            end_index += 20
            match_count += 20
            if match_count > match_limit:
                print(f'match limit hit for {guy.name}')
                break
            print(f'match count is {str(match_count)}, sleeping for {str(5+len(matches))}')
            time.sleep(5+len(matches))

def save_champs():
    with open('./db/champ_list.txt', 'w') as fp:
        champ_list = ["aatrox", "ahri", "akali", "akshan", "alistar", "amumu", "anivia", "annie", "aphelios", "ashe", "aurelion sol", "azir", "bard", "blitzcrank", "brand", "braum", "caitlyn", "camille", "cassiopeia", "cho'gath", "corki", "darius", "diana", "draven", "dr. mundo", "ekko", "elise", "evelynn", "ezreal", "fiddlesticks", "fiora", "fizz", "galio", "gangplank", "garen", "gnar", "gragas", "graves", "gwen", "hecarim", "heimerdinger", "illaoi", "irelia", "ivern", "janna", "jarvan iv", "jax", "jayce", "jhin", "jinx", "kai'sa", "kalista", "karma", "karthus", "kassadin", "katarina", "kayle", "kayn", "kennen", "kha'zix", "kindred", "kled", "kog'maw", "leblanc", "lee sin", "leona", "lillia", "lissandra", "lucian", "lulu", "lux", "malphite", "malzahar", "maokai", "master yi", "miss fortune", "wukong", "mordekaiser", "morgana", "nami", "nasus", "nautilus", "neeko", "nidalee", "nocturne", "nunu & willump", "olaf", "orianna", "ornn", "pantheon", "poppy", "pyke", "qiyana", "quinn", "rakan", "rammus", "rek'sai", "rell", "renata glasc", "renekton", "rengar", "riven", "rumble", "ryze", "samira", "sejuani", "senna", "seraphine", "sett", "shaco", "shen", "shyvana", "singed", "sion", "sivir", "skarner", "sona", "soraka", "swain", "sylas", "syndra", "tahm kench", "taliyah", "talon", "taric", "teemo", "thresh", "tristana", "trundle", "tryndamere", "twisted fate", "twitch", "udyr", "urgot", "varus", "vayne", "veigar", "vel'koz", "vex", "vi", "viego", "viktor", "vladimir", "volibear", "warwick", "xayah", "xerath", "xin zhao", "yasuo", "yone", "yorick", "yuumi", "zac", "zed", "zeri", "ziggs", "zilean", "zoe", "zyra"]
        json.dump(champ_list,fp)


def select_champ(search_term: str):
    """Select a champion from the champion list from a search term."""
    with open('./db/champ_list.txt', 'r') as fp:
        champ_list = json.load(fp)
    search_term = search_term.lower()
    selected_champ = [match for match in champ_list if re.findall(f"{search_term}.*",match)]
    if not selected_champ:
        selected_champ = [match for match in champ_list if re.findall(f"{search_term}.*",match.replace("'",""))]
    if not selected_champ:
        for champ in champ_list:
            if len(champ.split()) > 1:
                if champ.split()[0][0] == search_term[0] and champ.split()[1][0] == search_term[1]:
                    selected_champ = champ
    if type(selected_champ) is list:
        selected_champ = selected_champ[0]
    return selected_champ if selected_champ else None

def diffgame(champion):
    """Get champion winrate from Kierke's API."""
    champion = select_champ(champion)
    if not champion:
        return 'Champion not found.'

    url = f"https://differentgame.gg/api/champs.json"
    source = requests.get(url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}).json()

    champs = source[0]

    total_enemy_games = champs[champion]['ewin'] + champs[champion]['eloss']
    total_ally_games = champs[champion]['awin'] + champs[champion]['aloss']

    enemy_winrate = champs[champion]['ewin'] / total_enemy_games * 100
    ally_winrate = champs[champion]['awin'] / total_ally_games * 100

    return f"{champion} has a {ally_winrate:.2f}% winrate as an ally({total_ally_games} games), and {enemy_winrate:.2f}% winrate as an enemy({total_enemy_games} games)."

def spec_check(player):
    with open('riot_token.txt') as fp:
        riot_token = fp.read()


    steven = cass.Summoner(name='YoRHa Destiny', region='NA')
    lucas = cass.Summoner(name='IAmMentallyIll', region='NA')

    default_settings = cass.get_default_config()
    default_settings['global']['default_region'] = 'NA'
    default_settings['global']['version_from_match'] = 'version'
    cass.apply_settings(default_settings)
    cass.set_riot_api_key(riot_token)

    gamer = lucas if player == 'mrmouton' else steven

    match = cass.get_current_match( region=cass.data.Region.north_america, summoner=gamer)
    
    match_total_seconds = int((match.duration).total_seconds())
    match_minutes = match_total_seconds // 60
    match_seconds = match_total_seconds % 60

    dest_part = match.participants[steven] if steven in match.participants else None
    moot_part = match.participants[lucas] if lucas in match.participants else None

    ally_team = dest_part.team if steven in match.participants else moot_part.team
    enemy_team = [team for team in match.teams if team != ally_team][0]

    gamers = [dest_part, moot_part]
    ally_champs = []
    enemy_champs = []


    for player in ally_team.participants:
        if player not in gamers:
            ally_champs.append(player.champion.name.lower())

    for player in enemy_team.participants:
        enemy_champs.append(player.champion.name.lower())

    ally_winrates = []
    enemy_winrates = []

    for champ in ally_champs:
        ally_winrates.append(champ_winrate(champ, mode='ally'))

    ally_team_winrate = sum(ally_winrates) / len(ally_winrates)

    for champ in enemy_champs:
        enemy_winrates.append(champ_winrate(champ, mode='enemy'))

    enemy_team_winrate = sum(enemy_winrates) / len(enemy_winrates)

    # return f"Considering moot/steve matches, the ally team's champion winrate is: {ally_team_winrate:.2f}%, enemy team's champion winrate is {enemy_team_winrate:.2f}%. Moot/Steve's winrate for matches longer than {match_minutes}:{match_seconds} is {duration_winrate(match_total_seconds)} (this is of questionable value)."
    return f"Considering moot/steve matches, the ally team's champion winrate is: {ally_team_winrate:.2f}%, enemy team's champion winrate is {enemy_team_winrate:.2f}%"


if __name__ == "__main__":
    load_history()