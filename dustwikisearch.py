import requests, time, glob, os
from bs4 import BeautifulSoup
from framedatabase import *


def char_select(search_term):
    rosterlist = ['Anji Mito', 'Axl Low', 'Chipp Zanuff', 'Faust', 'Giovanna', 'Goldlewis Dickinson', 'I-No', 'Jack-O', 'Ky Kiske', 'Leo Whitefang', 'May', 'Millia Rage', 'Nagoriyuki', 'Potemkin', 'Ramlethal Valentine', 'Sol Badguy', 'Zato-1']
    result = [match for match in rosterlist if search_term.title() in match]
    return result[0]


def scrape_data(character):

    char_raw = char_select(character)
    char_parsed_url = char_raw.title().replace(" ","_")
    char_parsed_sql = char_parsed_url.replace('-','_')

    url = f'https://www.dustloop.com/wiki/index.php?title=GGST/{char_parsed_url}/Frame_Data'

    r = requests.get(url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})

    c = r.content

    soup = BeautifulSoup(c, 'lxml')

    tables = soup.find_all("table", class_="cargoDynamicTable display")



    

    normal_move_rows = tables[0].find_all("tr")
    normal_headers_raw = normal_move_rows[1].text.split()
    normal_headers = [header.lower() for header in normal_headers_raw]

    connect(char_parsed_sql,'normals', normal_headers)

    for row in normal_move_rows[2:]:
        datas = row.find_all("td")
        newlist = [entry.text for entry in datas[1:]]
        insert_data(char_parsed_sql, 'normals', normal_headers, newlist)

    special_move_rows = tables[1].find_all("tr")
    special_headers_raw = special_move_rows[1].text.split()
    special_headers = [header.lower() for header in special_headers_raw]

    connect(char_parsed_sql,'specials', special_headers)

    for row in special_move_rows[2:]:
        datas = row.find_all("td")
        newlist = [entry.text for entry in datas[1:]]
        try:
            insert_data(char_parsed_sql, 'specials', special_headers, newlist)
        except Exception as e:
            print(e)

    super_move_rows = tables[2].find_all("tr")
    super_headers_raw = super_move_rows[1].text.split()
    super_headers = [header.lower() for header in super_headers_raw]

    connect(char_parsed_sql,'supers', super_headers)

    for row in super_move_rows[2:]:
        datas = row.find_all("td")
        newlist = [entry.text for entry in datas[1:]]
        try:
            insert_data(char_parsed_sql, 'supers', super_headers, newlist)
        except Exception as e:
            print(e)

    other_move_rows = tables[3].find_all("tr")
    other_headers_raw = other_move_rows[1].text.split()
    other_headers = [header.lower() for header in other_headers_raw]

    connect(char_parsed_sql,'others', other_headers)

    for row in other_move_rows[2:]:
        datas = row.find_all("td")
        newlist = [entry.text for entry in datas[1:]]
        try:
            insert_data(char_parsed_sql, 'others', other_headers, newlist)
        except Exception as e:
            print(e)

def full_scrape():

    files = glob.glob('./db/*')
    for f in files:
        os.remove(f)

    rosterlist = ['Anji Mito', 'Axl Low', 'Chipp Zanuff', 'Faust', 'Giovanna', 'Goldlewis Dickinson', 'I-No', 'Jack-O', 'Ky Kiske', 'Leo Whitefang', 'May', 'Millia Rage', 'Nagoriyuki', 'Potemkin', 'Ramlethal Valentine', 'Sol Badguy', 'Zato-1']
    for character in rosterlist:
        try:
            print('scraping ' + character)
            scrape_data(character)
        except:
            print(character + ' failed to scrape.')
        time.sleep(5)




