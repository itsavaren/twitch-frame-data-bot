import requests, glob, os, json
from bs4 import BeautifulSoup
from dust_db import *


def scrape_data(game):

    #remove existing database files
    files = glob.glob(f'./db/{game}*.db')
    for f in files:
        os.remove(f)

    #set URL based on game selected
    if game == 'ggst':
        moves_url = f'https://www.dustloop.com/wiki/index.php?title=Special:CargoQuery&limit=1000&tables=MoveData_GGST&fields=_pageName%3DPage%2Cchara%3Dchara%2Cname%3Dname%2Cinput%3Dinput%2Cdamage%3Ddamage%2Cguard%3Dguard%2Cstartup%3Dstartup%2Cactive%3Dactive%2Crecovery%3Drecovery%2ConBlock%3DonBlock%2ConHit%3DonHit%2Clevel%3Dlevel%2Ccounter%3Dcounter%2Cimages__full%3Dimages%2Chitboxes__full%3Dhitboxes%2Cnotes__full%3Dnotes%2Ctype%3Dtype%2CriscGain%3DriscGain%2Cprorate%3Dprorate%2Cinvuln%3Dinvuln%2Ccancel%3Dcancel&max+display+chars=300'
        char_url = f'https://www.dustloop.com/wiki/index.php?title=Special:CargoTables/ggstCharacters'
    elif game =='bbcf':
        moves_url = f'https://www.dustloop.com/wiki/index.php?title=Special:CargoQuery&limit=3000&tables=MoveData_BBCF&fields=_pageName%3DPage%2Cchara%3Dchara%2Cname%3Dname%2Cinput%3Dinput%2Cdamage%3Ddamage%2Cguard%3Dguard%2Cstartup%3Dstartup%2Cactive%3Dactive%2Crecovery%3Drecovery%2ConBlock%3DonBlock%2Cattribute%3Dattribute%2Cinvuln%3Dinvuln%2Ccancel%3Dcancel%2Cp1%3Dp1%2Cp2%3Dp2%2Cstarter%3Dstarter%2Clevel%3Dlevel%2Cblockstun%3Dblockstun%2CgroundHit%3DgroundHit%2CairHit%3DairHit%2CgroundCH%3DgroundCH%2CairCH%3DairCH%2Cblockstop%3Dblockstop%2Chitstop%3Dhitstop%2CCHstop%3DCHstop%2Cimages__full%3Dimages%2Chitboxes__full%3Dhitboxes%2Ctype%3Dtype%2Cnotes__full%3Dnotes&max+display+chars=300'
        char_url = f'https://www.dustloop.com/wiki/index.php?title=Special:CargoTables/bbcfCharacters'
    elif game =='mbtl':
        moves_url = f'https://wiki.gbl.gg/index.php?title=Special:CargoQuery&limit=1000&tables=MBTL_MoveData&fields=_pageName%3DPage%2CmoveId%3DmoveId%2Cchara%3Dchara%2Cinput%3Dinput%2CinputInfo%3DinputInfo%2Cname%3Dname%2Csubtitle%3Dsubtitle%2Cimages__full%3Dimages%2Chitboxes__full%3Dhitboxes%2Cdamage%3Ddamage%2CminDamage%3DminDamage%2Cguard__full%3Dguard%2Ccancel__full%3Dcancel%2Cproperty__full%3Dproperty%2Ccost__full%3Dcost%2Cattribute__full%3Dattribute%2Cstartup%3Dstartup%2Cactive%3Dactive%2Crecovery%3Drecovery%2Clanding%3Dlanding%2Coverall%3Doverall%2CframeAdv%3DframeAdv%2Cinvul%3Dinvul&max+display+chars=300'
        char_url = None

    #create web request to dustloop move data cargo table, find tables in result, conditional on game selection
    r = requests.get(moves_url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
    c = r.content
    soup = BeautifulSoup(c, 'lxml')
    tables_list = soup.find_all("table")

    #get headers from table for database columns
    headers = [data.text.lower() for data in tables_list[0].find_all("th")]

    #extract rows from table
    data_rows = tables_list[0].find_all("tr")

    #create empty list to store moves
    move_list = []

    #create a list containing the entries from each row in order, replace some terms for ease of lookup, and append the resultant list to the move storage list
    for data_row in data_rows:
        move_data = [data.text.lower() for data in data_row.find_all("td")]
        move_data = [data.replace(' level ', '.') for data in move_data]
        move_data = [data.replace(' br', '.br') for data in move_data]
        move_data = [data.replace('di ', 'di.') for data in move_data]
        move_list.append(move_data)

    #remove the headers from the move list
    move_list.pop(0)

    #connect(and create if necessary) database, insert data into database table
    connect(game, headers)
    insert_data(game, move_list)

    try:
        #create web request to dustloop character data cargo table, find tables in result'
        r = requests.get(char_url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
        c = r.content
        soup = BeautifulSoup(c, 'lxml')
        tables_list = soup.find_all("table")

        #get headers from table for database columns
        headers = [data.text.lower().replace(' ', '_') for data in tables_list[0].find_all("th")]

        #extract rows from table
        data_rows = tables_list[0].find_all("tr")

        #create empty list to store characters
        character_list = []

        #create a list containing the entries from each row in order and append the resultant list to the character storage list
        for data_row in data_rows:
            move_data = [data.text.lower() for data in data_row.find_all("td")]
            character_list.append(move_data)

        #remove the headers from the character list
        character_list.pop(0)

        #connect to(and create if necessary) databases using headers as colum names, insert data into database table
        connect_chars(game, headers)
        insert_data_chars(game, character_list)
    except Exception as e:
        print(e)

    #read document of successful note edits, remove document, parse edits
    try:
        with open(f'./db/{game}_db_notes.txt', 'r') as fp:
            lines = fp.read().split(',')
        os.remove(f'./db/{game}_db_notes.txt')
        lines.remove('')
        lines = list(set(lines))
        for line in lines:
            parse_move(game, line)
    except Exception as e:
        print(e)

    #create character roster file
    databases = glob.glob('./db/*_framedata.db')
    name_list = {}
    for database in databases:
        conn =sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT chara FROM framedata')
        rows = cur.fetchall()
        name_list[database[5:9]] = listify(rows)
        conn.close()
    with open('./db/roster_list.json','w') as fp:
        json.dump(name_list,fp, indent=4)

def erase_data(game):
    files = glob.glob(f'./db/{game}*')
    for f in files:
        os.remove(f)