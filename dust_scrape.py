import requests, glob, os
from bs4 import BeautifulSoup
from dust_db import *


def char_select(search_term):
    roster_list = ['Anji Mito', 'Axl Low', 'Chipp Zanuff', 'Faust', 'Giovanna', 'Goldlewis Dickinson', 'I-No', 'Jack-O', 'Ky Kiske', 'Leo Whitefang', 'May', 'Millia Rage', 'Nagoriyuki', 'Potemkin', 'Ramlethal Valentine', 'Sol Badguy', 'Zato-1']
    result = [match for match in roster_list if search_term.title() in match]
    return result[0]

def scrape_data(character):
    char_raw = char_select(character)
    char_parsed_url = char_raw.replace(" ","_")
    char_parsed_sql = char_parsed_url.replace('-','_').lower()

    url = f'https://www.dustloop.com/wiki/index.php?title=GGST/{char_parsed_url}/Data&action=pagevalues'
    r = requests.get(url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
    c = r.content

    soup = BeautifulSoup(c, 'lxml')

    tables_list = soup.find_all("table", class_="wikitable mw-page-info")

    move_list = []

    for table in tables_list:
        data_rows = table.find_all("tr")
        move_dict = {}
        for row in data_rows:
            data_cells = row.find_all("td")
            move_dict[data_cells[0].text.lower()] = data_cells[1].text.lower()
        if 'chara' not in move_dict.keys():
            continue
        del move_dict['images'], move_dict['hitboxes']
        move_list.append(move_dict)
    connect(char_parsed_sql, move_list)
    insert_data(char_parsed_sql, move_list)


def full_scrape():
    files = glob.glob('./db2/*')
    for f in files:
        os.remove(f)
    rosterlist = ['Anji Mito', 'Axl Low', 'Chipp Zanuff', 'Faust', 'Giovanna', 'Goldlewis Dickinson', 'I-No', 'Jack-O', 'Ky Kiske', 'Leo Whitefang', 'May', 'Millia Rage', 'Nagoriyuki', 'Potemkin', 'Ramlethal Valentine', 'Sol Badguy', 'Zato-1']
    for char in rosterlist:
        scrape_data(char)