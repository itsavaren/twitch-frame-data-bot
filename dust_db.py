import sqlite3



def connect(character, move_dict_list):
    conn =sqlite3.connect(f'./db2/{character}.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS ' + character + '(%s)' % ', '.join(list(move_dict_list[0].keys())))
    conn.commit()
    conn.close()

def insert_data(character,move_dict_list):
    conn =sqlite3.connect(f'./db2/{character}.db')
    cur = conn.cursor()
    val_count = ('?,'*len(move_dict_list[0].keys()))[:-1]
    for move_dict in move_dict_list:
        cur.execute('INSERT INTO ' + character +' VALUES (%s)' % val_count, (*list(move_dict.values()),))
    conn.commit()
    conn.close()

def get_move_data(character, move_input):
    conn =sqlite3.connect(f'./db2/{character}.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM ' + character + ' WHERE input LIKE ?', ('%'+move_input+'%',))
    selected_by = 'input'
    row = cur.fetchall()
    if not row:
        cur.execute('SELECT * FROM ' + character + ' WHERE name LIKE ?', ('%'+move_input+'%',))
        selected_by = 'name'
        row = cur.fetchall()
    row = list(row[0])
    cur.execute('SELECT * FROM ' + character)
    labels = [cur[0] for cur in cur.description]
    conn.close()
    move_data = dict(zip(labels,row))
    # output = ''
    # for (name, data) in zip(labels, row):
	#     output += str(f'| {name}: {data} |')
    return str(f" {move_data[selected_by]} - startup: {move_data['startup']}, onblock: {move_data['onblock']}, onhit: {move_data['onhit']}")

def view(character, move_type):
    conn =sqlite3.connect(f'./db/{character}.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM ' + move_type)
    rows = cur.fetchall()
    conn.close()
    return rows

