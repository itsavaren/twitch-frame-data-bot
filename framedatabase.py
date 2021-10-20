import sqlite3

def connect(character, movetype, header_list):
    conn =sqlite3.connect(f'./db/{character}.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS ' + movetype + '(%s)' % ', '.join(header_list))
    conn.commit()
    conn.close()

def insert_data(character,movetype,header_list,values):
    conn =sqlite3.connect(f'./db/{character}.db')
    cur = conn.cursor()
    val_count = ('?,'*len(header_list))[:-1]
    cur.execute('INSERT INTO ' + movetype +' VALUES (%s)' % val_count, (*values,))
    conn.commit()
    conn.close()

def get_move_data(character, move_input):
    conn =sqlite3.connect(f'./db/{character}.db')
    cur = conn.cursor()
    move_types=['normals', 'specials', 'supers', 'others']
    for move_type in move_types:
        try:
            cur.execute('SELECT * FROM ' + move_type + ' WHERE input = ?', (move_input,))
            selected_by = 'input'
            row = cur.fetchall()
            if row:
                break
        except Exception as e:
            cur.execute('SELECT * FROM ' + move_type + ' WHERE name = ?', (move_input,))
            selected_by = 'name'
            row = cur.fetchall()
            if row:
                break
    if row:
        row = list(row[0])
        cur.execute('SELECT * FROM ' + move_type)
        labels = [cur[0] for cur in cur.description]
    conn.close()
    move_data = dict(zip(labels,row))
    # output = ''
    # for (name, data) in zip(labels, row):
	#     output += str(f'| {name}: {data} |')
    return str(f"{character} {move_data[selected_by]}: Startup {move_data['startup']}f, onhit: {move_data['onhit']}")

def view(character, move_type):
    conn =sqlite3.connect(f'./db/{character}.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM ' + move_type)
    rows = cur.fetchall()
    conn.close()
    return rows

