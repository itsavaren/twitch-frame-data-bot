import sqlite3
import json



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
    row = cur.fetchall()
    if not row:
        cur.execute('SELECT * FROM framedata WHERE name LIKE ? AND chara=?', ('%'+move_input+'%', character))
        selected_by = 'name'
        row = cur.fetchall()
    row = list(row[0])
    cur.execute('SELECT * FROM framedata')
    labels = [cur[0] for cur in cur.description]
    conn.close()
    move_data = dict(zip(labels,row))
    if detail == None:
        return str(f" {move_data[selected_by]} - startup: {move_data['startup']}, onblock: {move_data['onblock']}, onhit: {move_data['onhit']}")
    if 'detail' in detail:
        del move_data['page'], move_data['images'], move_data['hitboxes']
        return ', '.join([str(f'{keys}: {values}') for (keys, values) in move_data.items()])
    else:
        return str(f" {move_data[selected_by]} {detail}: {move_data[detail]}")

