import sqlite3
import json


def char_select(search_term):
    roster_list = ['anji mito', 'axl low', 'chipp zanuff', 'faust', 'giovanna', 'goldlewis dickinson', 'i-no', 'jack-o', 'ky kiske', 'leo whitefang', 'may', 'millia rage', 'nagoriyuki', 'potemkin', 'ramlethal valentine', 'sol badguy', 'zato-1']
    result = [match for match in roster_list if search_term.lower() in match]
    if result:
        return result[0]



def connect(headers):
    conn =sqlite3.connect(f'./db/framedata.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS framedata(%s)' % ', '.join(headers))
    conn.commit()
    conn.close()

def insert_data(move_list):
    conn =sqlite3.connect(f'./db/framedata.db')
    cur = conn.cursor()
    val_count = ('?,'*len(move_list[0]))[:-1]
    for move in move_list:
        try:
            cur.execute('INSERT INTO framedata VALUES (%s)' % val_count, (move))
        except Exception as e:
            print(e)
    conn.commit()
    conn.close()

def get_move_data(character, move_input, detail=None):
    conn =sqlite3.connect(f'./db/framedata.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM framedata WHERE input LIKE ? AND chara=?', (move_input+'%', character))
    selected_by = 'input'
    rows = cur.fetchall()
    if not rows:
        cur.execute('SELECT * FROM framedata WHERE name LIKE ? AND chara=?', ('%'+move_input+'%', character))
        selected_by = 'name'
        rows = cur.fetchall()
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
        return str(f"{move_data['chara']} {move_data['name']} {move_data['input']} - startup: {move_data['startup']}, onblock: {move_data['onblock']}, onhit: {move_data['onhit']}")
    if 'detail' in detail:
        del move_data['page'], move_data['images'], move_data['hitboxes']
        return ', '.join([str(f'{keys}: {values}') for (keys, values) in move_data.items()])
    else:
        return str(f"{move_data['chara']} {move_data[selected_by]} {detail}: {move_data[detail]}")



def parse_move(full_message):

    conn =sqlite3.connect(f'./db/framedata.db')
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT chara FROM framedata')
    rows = cur.fetchall()
    name_list = [list(data)[0] for data in rows]
    words = full_message.lower().split()

    cur.execute('SELECT * FROM framedata')
    labels = [cur[0] for cur in cur.description]
    if words[-1] in labels or 'detail' in words[-1]:
        specifier = words.pop()
    else:
        specifier = None

    if char_select(' '.join(words[:2])):
        character = [match for match in name_list if ' '.join(words[:2]) in match][0]
        words = words[2:]
    elif char_select(words[0]):
        character = [match for match in name_list if words[0] in match][0]
        words = words[1:]
    else:
        return "Character not found."


    cur.execute('SELECT DISTINCT input FROM framedata WHERE chara = ?', (character,))
    rows = cur.fetchall()
    move_input_list = [list(data)[0] for data in rows]
    if words[0] in move_input_list:
        query = words.pop(0)
    else:
        cur.execute('SELECT DISTINCT name FROM framedata WHERE chara = ?', (character,))
        rows = cur.fetchall()
        move_name_list = [list(data)[0] for data in rows]
        if not [match for match in move_name_list if ' '.join(words) in match]:
            return 'Query not in input or move list.'
        query = ' '.join(words)

    result = get_move_data(character, query, specifier)
    conn.close()
    return result

parse_move('ky foudre')