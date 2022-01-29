import sqlite3, glob, json


def limit_length(raw_string):
    if len(raw_string) > 100:
        return raw_string[:100]+"..."
    else:
        return raw_string

def listify(sql_rows):
    return [list(data)[0] for data in sql_rows]


def char_select(search_term):
    with open('./db/roster_list.json','r') as fp:
        roster_list = json.load(fp)

    results = {}

    for key, value in roster_list.items():
        matches = [match for match in value if search_term.lower() in match]
        if matches:
            results[key] = matches
    
    if results:
        return results
    else:
        return None

# def char_select(game, search_term):
#     conn =sqlite3.connect(f'./db/{game}_framedata.db')
#     cur = conn.cursor()
#     cur.execute('SELECT DISTINCT chara FROM framedata')
#     rows = cur.fetchall()
#     name_list = [list(data)[0] for data in rows]
#     conn.close()
#     result = [match for match in name_list if search_term.lower() in match]
#     if result:
#         if len(result) == 1:
#             return result[0]
#         else:
#             return result
#     else:
#         return None

def connect(game, headers):
    conn =sqlite3.connect(f'./db/{game}_framedata.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS framedata(%s)' % ', '.join(headers))
    conn.commit()
    conn.close()

def connect_chars(game, headers):
    conn =sqlite3.connect(f'./db/{game}_characters.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS characters(%s)' % ', '.join(headers))
    conn.commit()
    conn.close()
    

def insert_data(game, move_list):
    conn =sqlite3.connect(f'./db/{game}_framedata.db')
    cur = conn.cursor()
    val_count = ('?,'*len(move_list[0]))[:-1]
    for move in move_list:
        try:
            cur.execute('INSERT INTO framedata VALUES (%s)' % val_count, (move))
        except Exception as e:
            print(e)
    conn.commit()
    conn.close()

def update_note(game, character, move, note):
    conn =sqlite3.connect(f'./db/{game}_framedata.db')
    cur = conn.cursor()
    cur.execute("UPDATE framedata SET notes=? WHERE chara=? AND input=?",(note,character,move))
    conn.commit()
    conn.close()

def insert_data_chars(game, move_list):
    conn =sqlite3.connect(f'./db/{game}_characters.db')
    cur = conn.cursor()
    val_count = ('?,'*len(move_list[0]))[:-1]
    for move in move_list:
        try:
            cur.execute('INSERT INTO characters VALUES (%s)' % val_count, (move))
        except Exception as e:
            print(e)
    conn.commit()
    conn.close()

def get_move_data(game, character, move_input, detail=None):
    conn =sqlite3.connect(f'./db/{game}_framedata.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM framedata WHERE input LIKE ? AND chara=?', (move_input, character))
    rows = cur.fetchall()
    if not rows:
        cur.execute('SELECT * FROM framedata WHERE input LIKE ? AND chara=?', (move_input+'%', character))
        rows = cur.fetchall()
    selected_by = 'input'
    if not rows:
        cur.execute('SELECT * FROM framedata WHERE name LIKE ? AND chara=?', ('%'+move_input.replace(' ','%')+'%', character))
        selected_by = 'name'
        rows = cur.fetchall()
    if not rows:
        return 'No matching result for move input or name.'
    move_list = [list(data) for data in rows]
    cur.execute('SELECT * FROM framedata')
    labels = [cur[0] for cur in cur.description]
    conn.close()
    move_dicts = [dict(zip(labels,row)) for row in move_list]
    if len(move_dicts) > 4:
        return str(f"More than 4 moves were found by {selected_by} for {move_input}. Be more specific")
    if len(move_dicts) > 1 and selected_by == 'input':
        return str(f"More than one move found by input:{[move_data['input']+': '+move_data['name'] for move_data in move_dicts]}")
    elif len(move_dicts) > 1 and selected_by == 'name':
        return str(f"More than one move found by name:{[move_data['name']+': '+move_data['input'] for move_data in move_dicts]}")
    else:
        move_data = move_dicts[0]
    if detail == None:
        if game == 'ggst':
            return str(f"{move_data['chara']} {move_data['name']} {move_data['input']} - startup: {move_data['startup']}, onblock: {move_data['onblock']}, onhit: {move_data['onhit']}")
        elif game == 'bbcf':
            return str(f"{move_data['chara']} {move_data['name']} {move_data['input']} - startup: {move_data['startup']}, onblock: {move_data['onblock']}")
        elif game == 'mbtl':
            return str(f"{move_data['chara']} {move_data['name']} {move_data['input']} - startup: {move_data['startup']}, advantage: {move_data['frameadv']}")
    
    if 'detail' in detail:
        del move_data['page'], move_data['images'], move_data['hitboxes']
        return ', '.join([str(f'{keys}: {values}') for (keys, values) in move_data.items()])
    else:
        return str(f"{move_data['chara']} {move_data[selected_by]} {detail}: {move_data[detail]}")

    
def get_char_data(game, character, detail= None):
    conn =sqlite3.connect(f'./db/{game}_characters.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM characters WHERE name LIKE ?', (character,))
    rows = cur.fetchall()
    char_list = [list(data) for data in rows]
    cur.execute('SELECT * FROM characters')
    labels = [cur[0] for cur in cur.description]    
    char_dict = [dict(zip(labels,row)) for row in char_list][0]
    conn.close()
    if detail == None:
        return str(f"{char_dict['name']}  - defense: {char_dict['defense']}, guts: {char_dict['guts']}, weight: {char_dict['weight']}, backdash: {char_dict['backdash']}")
    if 'detail' in detail:
        del char_dict['page'], char_dict['portrait'], char_dict['icon']
        return ', '.join([str(f'{keys}: {values}') for (keys, values) in char_dict.items()])
    else:
        return str(f"{char_dict['name']} {detail}: {char_dict[detail]}")    


def parse_move(full_message):

    games= []
    words = full_message.lower().split()


    if words[0] in ['ggst','bbcf']:
        games = words.pop(0)

    first_two = char_select(' '.join(words[:2]))
    first_word = char_select(words[0])

    if first_two:
        characters = first_two
        words = words[2:]
    elif char_select(words[0]):
        characters = first_word
        words = words[1:]
    else:
        print("Character not found.")

    for key in characters.keys():
        games.append(key)

    if len(games) == 1:
        selected_game = games[0]
        character = [character for character in characters.values()][0]
        if len(characters) > 1:
            return f'multiple characters found in {selected_game}: ' + ', '.join(characters)
        else:
            character = character[0]
    else:
        return f'multiple games found, specify game: "example: !fd ggst may 5h"'


    conn =sqlite3.connect(f'./db/{selected_game}_framedata.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM framedata')
    move_headers = [cur[0] for cur in cur.description]

    conn2 = sqlite3.connect(f'./db/{selected_game}_characters.db')
    cur2 = conn2.cursor()
    cur2.execute('SELECT * FROM characters')
    char_headers = [cur2[0] for cur2 in cur2.description]
    conn2.close()


    if words[-1] in move_headers or words[-1] in char_headers or 'detail' in words[-1]:
        specifier = words.pop()
    else:
        specifier = None




    

    if 'info' in words:
        return get_char_data(selected_game, character, specifier)

    if words[0] == 'update':
        conn.close()
        with open(f'./db/{selected_game}_db_notes.txt', 'a') as fp:
            fp.write(full_message+',')
        update_note(selected_game   , character, words[1],' '.join(words[2:]))
        return f'{character} {words[1]} notes updated.'

    if type(character) == list:
        return f"{len(character)} characters found:{' ,'.join(character)}"

    cur.execute('SELECT DISTINCT input FROM framedata WHERE chara = ?', (character,))
    rows = cur.fetchall()
    move_input_list = [list(data)[0] for data in rows]
    if words[0] in move_input_list:
        query = words.pop(0)
    else:
        cur.execute('SELECT DISTINCT name FROM framedata WHERE chara = ?', (character,))
        rows = cur.fetchall()
        query = ' '.join(words)

    result = get_move_data(selected_game, character, query, specifier)
    conn.close()
    return result