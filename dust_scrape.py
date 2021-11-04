import requests, glob, os
from bs4 import BeautifulSoup
from dust_db import *


def char_select(search_term):
    roster_list = ['anji mito', 'axl low', 'chipp zanuff', 'faust', 'giovanna', 'goldlewis dickinson', 'i-no', 'jack-o', 'ky kiske', 'leo whitefang', 'may', 'millia rage', 'nagoriyuki', 'potemkin', 'ramlethal valentine', 'sol badguy', 'zato-1']
    result = [match for match in roster_list if search_term.lower() in match]
    return result[0]


def scrape_data():
    files = glob.glob('./db/*')
    for f in files:
        os.remove(f)
    url = f'https://www.dustloop.com/wiki/index.php?title=Special:CargoQuery&limit=1000&tables=MoveData_GGST&fields=_pageName%3DPage%2Cchara%3Dchara%2Cname%3Dname%2Cinput%3Dinput%2Cdamage%3Ddamage%2Cguard%3Dguard%2Cstartup%3Dstartup%2Cactive%3Dactive%2Crecovery%3Drecovery%2ConBlock%3DonBlock%2ConHit%3DonHit%2Clevel%3Dlevel%2Ccounter%3Dcounter%2Cimages__full%3Dimages%2Chitboxes__full%3Dhitboxes%2Cnotes__full%3Dnotes%2Ctype%3Dtype%2CriscGain%3DriscGain%2Cprorate%3Dprorate%2Cinvuln%3Dinvuln%2Ccancel%3Dcancel&max+display+chars=300'
    r = requests.get(url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
    c = r.content

    soup = BeautifulSoup(c, 'lxml')

    tables_list = soup.find_all("table")

    headers = [data.text.lower() for data in tables_list[0].find_all("th")]

    data_rows = tables_list[0].find_all("tr")

    move_list = []

    for data_row in data_rows:
        move_data = [data.text.lower() for data in data_row.find_all("td")]
        move_list.append(move_data)

    move_list.pop(0)

    connect(headers)
    insert_data(move_list)
