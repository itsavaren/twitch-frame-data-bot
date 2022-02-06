from bs4 import BeautifulSoup
import requests


def get_rank(raw_name, region='na'):
    name = raw_name.replace(' ','%20')
    name = f"https://{region}.op.gg/summoner/userName=" + name
    source = requests.get(name, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}).text
    soup = BeautifulSoup(source, "lxml")
    lp = soup.find("span", {"class": "LeaguePoints"}).getText()
    rank = soup.find("div", {"class": "TierRank"}).getText()
    lp = lp.replace('\t','').replace('\n','')
    return f"According to op.gg, {raw_name}'s rank is {rank}, {lp}"
