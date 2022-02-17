import requests, json, re
import cassiopeia as cass
import sqlite3, time
import requests
import ujson
requests.models.complexjson = ujson



def connect():
    """Connect to the database and create the table if necessary."""
    #open the database file
    conn =sqlite3.connect(f'./db/match_history.db')
    #create cursor
    cur = conn.cursor()
    #create the table if it isn't in there
    cur.execute('''CREATE TABLE IF NOT EXISTS matches(match_id TEXT PRIMARY KEY, player TEXT, first_drake INTEGER, first_blood INTEGER, win INTEGER,
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

def champ_winrate(champion):
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

    return f"{champion} has a {ally_winrate:.2f}% winrate as an ally(in {total_ally_games} games), and {enemy_winrate:.2f}% winrate as an enemy(in {total_enemy_games} games)."
    
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
        match_limit = 100
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

    empties = 0
    begin_index = 0
    end_index = 40
    match_count = 0

    for guy in history_targets:
        while True:
            try:
                print('scanning')

                mrm_history = cass.get_match_history(begin_index=begin_index, end_index=end_index, region=cass.data.Region.north_america,
                                                        queue=cass.data.Queue.ranked_solo_fives, puuid=guy.puuid,
                                                        continent=cass.data.Continent.americas)

                

                matches = []

                for match in mrm_history:
                    try:
                        if match.patch.major < '11':
                            print('patch too old, breaking')
                            break

                        match_id = match.id
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

                        sql_list = [match_id, player, ally_team_dict['first_drake'], ally_team_dict['first_blood'], ally_team_dict['win'], moot_champ, dest_champ, offrole,
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

            if len(matches) != 10:
                print(f'length is {str(len(matches))} wrong, breaking')
            print(f"inserting {guy.name}'s games")


            connect()
            try:
                insert_data(matches)
            except Exception as e:
                print(f'insertion error: {e}')
                empties += 1
                if empties >4:
                    empties = 0
                    break
            print('sleeping')
            if match_count > match_limit:
                break
            time.sleep(60)
            begin_index += 40
            end_index += 40
            match_count += 40

def save_champs():
    with open('./db/champ_list.txt', 'w') as fp:
        champ_list = ["aatrox", "ahri", "akali", "akshan", "alistar", "amumu", "anivia", "annie", "aphelios", "ashe", "aurelion sol", "azir", "bard", "blitzcrank", "brand", "braum", "caitlyn", "camille", "cassiopeia", "cho'gath", "corki", "darius", "diana", "draven", "dr. mundo", "ekko", "elise", "evelynn", "ezreal", "fiddlesticks", "fiora", "fizz", "galio", "gangplank", "garen", "gnar", "gragas", "graves", "gwen", "hecarim", "heimerdinger", "illaoi", "irelia", "ivern", "janna", "jarvan iv", "jax", "jayce", "jhin", "jinx", "kai'sa", "kalista", "karma", "karthus", "kassadin", "katarina", "kayle", "kayn", "kennen", "kha'zix", "kindred", "kled", "kog'maw", "leblanc", "lee sin", "leona", "lillia", "lissandra", "lucian", "lulu", "lux", "malphite", "malzahar", "maokai", "master yi", "miss fortune", "wukong", "mordekaiser", "morgana", "nami", "nasus", "nautilus", "neeko", "nidalee", "nocturne", "nunu & willump", "olaf", "orianna", "ornn", "pantheon", "poppy", "pyke", "qiyana", "quinn", "rakan", "rammus", "rek'sai", "rell", "renata glasc", "renekton", "rengar", "riven", "rumble", "ryze", "samira", "sejuani", "senna", "seraphine", "sett", "shaco", "shen", "shyvana", "singed", "sion", "sivir", "skarner", "sona", "soraka", "swain", "sylas", "syndra", "tahm kench", "taliyah", "talon", "taric", "teemo", "thresh", "tristana", "trundle", "tryndamere", "twisted fate", "twitch", "udyr", "urgot", "varus", "vayne", "veigar", "vel'koz", "vex", "vi", "viego", "viktor", "vladimir", "volibear", "warwick", "xayah", "xerath", "xin zhao", "yasuo", "yone", "yorick", "yuumi", "zac", "zed", "zeri", "ziggs", "zilean", "zoe", "zyra"]
        json.dump(champ_list,fp)


def select_champ(search_term: str):
    """Select a champion from the champion list from a search term."""
    with open('./db/champ_list.txt', 'r') as fp:
        champ_list = json.load(fp)
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





    

        