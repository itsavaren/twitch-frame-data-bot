import requests, json
from time import sleep
from pymongo import MongoClient
from dust_db import *


def replace_many(target: str, mutator_tuples: list) -> list:
    """Replace multiple items in a single string"""
    for original, mutated in mutator_tuples:
        target = target.replace(original, mutated)
    return target


def format_moves(unformatted_list: list) -> list:
    """Lowercase and reformat some character specific inputs."""
    move_list = []
    for move in unformatted_list:
        move = {k.lower(): v for k, v in move.items()}
        move = {k: v.lower() if type(v) == str else v for k, v in move.items()}
        move = {
            k: replace_many(
                v, [(" level ", "."), ("\\", ""), ("di ", "di."), (" br", ".br")]
            )
            if type(v) == str
            else v
            for k, v in move.items()
        }

        move_list.append(move)
    return move_list


def format_chars(unformatted_list: list) -> list:
    """Lowercase and reformats some character statistics."""

    char_list = []
    for char in unformatted_list:
        char = {k.lower(): v for k, v in char.items()}
        char = {k: v.lower() if type(v) == str else v for k, v in char.items()}
        char = {k: round(v, 2) if type(v) == float else v for k, v in char.items()}
        char = {
            k: v.replace("\\", "") if type(v) == str else v for k, v in char.items()
        }

        char_list.append(char)
    final_list = [item for item in char_list if "tension" not in item["name"]]
    return final_list


def import_data(db_address: str, game: str):
    """Import data for the selected game."""

    db_client = MongoClient(db_address)

    # set cargoquery json URL based on game selected
    match game:
        case "ggst":
            moves_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=MoveData_GGST&&fields=chara%3Dchara%2Cname%3Dname%2Cinput%3Dinput%2Cdamage%3Ddamage%2Cguard%3Dguard%2Cstartup%3Dstartup%2Cactive%3Dactive%2Crecovery%3Drecovery%2ConBlock%3DonBlock%2ConHit%3DonHit%2Clevel%3Dlevel%2Ccounter%3Dcounter%2Cnotes__full%3Dnotes%2Ctype%3Dtype%2CriscGain%3DriscGain%2CriscLoss%3DriscLoss%2CwallDamage%3DwallDamage%2CinputTension%3DinputTension%2Cprorate%3Dprorate%2Cinvuln%3Dinvuln%2Ccancel%3Dcancel&&order+by=%60chara%60%2C%60name%60%2C%60input%60%2C%60damage%60%2C%60guard%60&limit=5000&format=json"
            char_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=ggstCharacters%2C&&fields=ggstCharacters.name%2C+ggstCharacters.defense%2C+ggstCharacters.guts%2C+ggstCharacters.guardBalance%2C+ggstCharacters.prejump%2C+ggstCharacters.weight%2C+ggstCharacters.backdash%2C+ggstCharacters.forwarddash%2C+ggstCharacters.movement_tension%2C+ggstCharacters.jump_duration%2C+ggstCharacters.high_jump_duration%2C+ggstCharacters.jump_height%2C+ggstCharacters.high_jump_height%2C+ggstCharacters.walk_speed%2C+ggstCharacters.back_walk_speed%2C+ggstCharacters.dash_initial_speed%2C+ggstCharacters.dash_acceleration%2C+ggstCharacters.dash_friction%2C&&order+by=%60cargo__ggstCharacters%60.%60name%60%2C%60cargo__ggstCharacters%60.%60defense%60%2C%60cargo__ggstCharacters%60.%60guts%60%2C%60cargo__ggstCharacters%60.%60guardBalance%60%2C%60cargo__ggstCharacters%60.%60prejump%60&limit=5000&format=json"
        case "gbvs":
            moves_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=MoveData_GBVS%2C&&fields=MoveData_GBVS.chara%2C+MoveData_GBVS.name%2C+MoveData_GBVS.input%2C+MoveData_GBVS.damage%2C+MoveData_GBVS.guard%2C+MoveData_GBVS.startup%2C+MoveData_GBVS.active%2C+MoveData_GBVS.recovery%2C+MoveData_GBVS.onBlock%2C+MoveData_GBVS.onHit%2C+MoveData_GBVS.attribute%2C+MoveData_GBVS.level%2C+MoveData_GBVS.blockstun%2C+MoveData_GBVS.groundHit%2C+MoveData_GBVS.airHit%2C+MoveData_GBVS.hitstop%2C+MoveData_GBVS.invuln%2C+MoveData_GBVS.type%2C+MoveData_GBVS.notes%2C&&order+by=%60cargo__MoveData_GBVS%60.%60chara%60%2C%60cargo__MoveData_GBVS%60.%60name%60%2C%60cargo__MoveData_GBVS%60.%60input%60%2C%60cargo__MoveData_GBVS%60.%60damage%60%2C%60cargo__MoveData_GBVS%60.%60guard%60&limit=5000&format=json"
            char_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=gbvsCharacters%2C&&fields=gbvsCharacters.name%2C+gbvsCharacters.health%2C+gbvsCharacters.prejump%2C+gbvsCharacters.backdash%2C&&order+by=%60cargo__gbvsCharacters%60.%60name%60%2C%60cargo__gbvsCharacters%60.%60health%60%2C%60cargo__gbvsCharacters%60.%60prejump%60%2C%60cargo__gbvsCharacters%60.%60backdash%60&limit=5000&format=json"
        case "bbcf":
            moves_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=MoveData_BBCF%2C&&fields=MoveData_BBCF.chara%2C+MoveData_BBCF.name%2C+MoveData_BBCF.input%2C+MoveData_BBCF.damage%2C+MoveData_BBCF.guard%2C+MoveData_BBCF.startup%2C+MoveData_BBCF.active%2C+MoveData_BBCF.recovery%2C+MoveData_BBCF.onBlock%2C+MoveData_BBCF.attribute%2C+MoveData_BBCF.invuln%2C+MoveData_BBCF.cancel%2C+MoveData_BBCF.p1%2C+MoveData_BBCF.p2%2C+MoveData_BBCF.starter%2C+MoveData_BBCF.level%2C+MoveData_BBCF.blockstun%2C+MoveData_BBCF.groundHit%2C+MoveData_BBCF.airHit%2C+MoveData_BBCF.groundCH%2C+MoveData_BBCF.airCH%2C+MoveData_BBCF.blockstop%2C+MoveData_BBCF.hitstop%2C+MoveData_BBCF.CHstop%2C+MoveData_BBCF.type%2C+MoveData_BBCF.notes%2C&&order+by=%60cargo__MoveData_BBCF%60.%60chara%60%2C%60cargo__MoveData_BBCF%60.%60name%60%2C%60cargo__MoveData_BBCF%60.%60input%60%2C%60cargo__MoveData_BBCF%60.%60damage%60%2C%60cargo__MoveData_BBCF%60.%60guard%60&limit=5000&format=json"
            char_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=bbcfCharacters%2C&&fields=bbcfCharacters.name%2C+bbcfCharacters.health%2C+bbcfCharacters.prejump%2C+bbcfCharacters.backdash%2C+bbcfCharacters.forwarddash%2C+bbcfCharacters.umo%2C&&order+by=%60cargo__bbcfCharacters%60.%60name%60%2C%60cargo__bbcfCharacters%60.%60health%60%2C%60cargo__bbcfCharacters%60.%60prejump%60%2C%60cargo__bbcfCharacters%60.%60backdash%60%2C%60cargo__bbcfCharacters%60.%60forwarddash%60&limit=5000&format=json"
        case "p4u2":
            moves_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=MoveData_P4U2%2C&&fields=MoveData_P4U2.chara%2C+MoveData_P4U2.name%2C+MoveData_P4U2.input%2C+MoveData_P4U2.damage%2C+MoveData_P4U2.guard%2C+MoveData_P4U2.startup%2C+MoveData_P4U2.active%2C+MoveData_P4U2.recovery%2C+MoveData_P4U2.onBlock%2C+MoveData_P4U2.attribute%2C+MoveData_P4U2.invuln%2C+MoveData_P4U2.cancel%2C+MoveData_P4U2.p1%2C+MoveData_P4U2.p2%2C+MoveData_P4U2.smp%2C+MoveData_P4U2.level%2C+MoveData_P4U2.type%2C+MoveData_P4U2.notes%2C&&order+by=%60cargo__MoveData_P4U2%60.%60chara%60%2C%60cargo__MoveData_P4U2%60.%60name%60%2C%60cargo__MoveData_P4U2%60.%60input%60%2C%60cargo__MoveData_P4U2%60.%60damage%60%2C%60cargo__MoveData_P4U2%60.%60guard%60&limit=5000&format=json"
            char_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=p4u2Characters%2C&&fields=p4u2Characters.name%2C+p4u2Characters.health%2C+p4u2Characters.prejump%2C+p4u2Characters.backdash%2C+p4u2Characters.comborate%2C+p4u2Characters.personacards%2C+p4u2Characters.umo%2C&&order+by=%60cargo__p4u2Characters%60.%60name%60%2C%60cargo__p4u2Characters%60.%60health%60%2C%60cargo__p4u2Characters%60.%60prejump%60%2C%60cargo__p4u2Characters%60.%60backdash%60%2C%60cargo__p4u2Characters%60.%60comborate%60&limit=5000&format=json"
        case "dnfd":
            moves_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=MoveData_DNFD%2C&&fields=MoveData_DNFD.chara%2C+MoveData_DNFD.name%2C+MoveData_DNFD.input%2C+MoveData_DNFD.damage%2C+MoveData_DNFD.guard%2C+MoveData_DNFD.startup%2C+MoveData_DNFD.recovery%2C+MoveData_DNFD.onBlock%2C+MoveData_DNFD.onHit%2C+MoveData_DNFD.notes%2C+MoveData_DNFD.type%2C+MoveData_DNFD.prorate%2C+MoveData_DNFD.invuln%2C+MoveData_DNFD.cancel%2C+MoveData_DNFD.MPcost%2C&&order+by=%60cargo__MoveData_DNFD%60.%60chara%60%2C%60cargo__MoveData_DNFD%60.%60name%60%2C%60cargo__MoveData_DNFD%60.%60input%60%2C%60cargo__MoveData_DNFD%60.%60damage%60%2C%60cargo__MoveData_DNFD%60.%60guard%60&limit=5000&format=json"
            char_url = f"https://www.dustloop.com/wiki/index.php?title=Special:CargoExport&tables=dnfdCharacters%2C&&fields=dnfdCharacters.name%2C+dnfdCharacters.health%2C+dnfdCharacters.prejump%2C+dnfdCharacters.backdash%2C+dnfdCharacters.forwarddash%2C+dnfdCharacters.umo%2C&&order+by=%60cargo__dnfdCharacters%60.%60name%60%2C%60cargo__dnfdCharacters%60.%60health%60%2C%60cargo__dnfdCharacters%60.%60prejump%60%2C%60cargo__dnfdCharacters%60.%60backdash%60%2C%60cargo__dnfdCharacters%60.%60forwarddash%60&limit=5000&format=json"
        case _:
            raise Exception("Game not found.")

    # create web request to dustloop move data cargo table, find tables in result, conditional on game selection
    r = requests.get(
        moves_url,
        headers={
            "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
        },
    )

    if not r.ok:
        raise Exception("Dustloop cargo query response failure.")

    move_list = format_moves(r.json())

    mongo = db_client

    db = mongo["moves"]
    moves_db = db[game]

    for entry in move_list:
        try:
            moves_db.update_one(
                {"$and": [{"chara": entry["chara"]}, {"input": entry["input"]}]},
                {"$set": entry},
                upsert=True,
            )
        except KeyError as e:
            moves_db.update_one(
                {"$and": [{"chara": entry["chara"]}, {"name": entry["name"]}]},
                {"$set": entry},
                upsert=True,
            )

    #############################################################
    # create web request to dustloop character data cargo table, find tables in result'

    r = requests.get(
        char_url,
        headers={
            "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
        },
    )

    if not r.ok:
        raise Exception("Dustloop cargo query response failure.")

    char_list = format_chars(r.json())

    # mongo = MongoClient(db_address)
    db = mongo["chars"]
    chars_db = db[game]

    for entry in char_list:
        chars_db.update_one({"name": entry["name"]}, {"$set": entry}, upsert=True)

    # create character roster file

    try:
        with open("./db/roster_list.json", "r") as fp:
            chars = json.load(fp)
    except:
        chars = {}

    chars[game] = [char["name"] for char in chars_db.find()]

    with open("./db/roster_list.json", "w") as fp:
        json.dump(chars, fp, indent=4)

    db_client.close()


def erase_data(db_address: str, game: str):
    """Clear all collections."""

    db_client = MongoClient(db_address)
    db = db_client["moves"]
    moves_db = db[game]
    moves_db.drop()
    db = db_client["chars"]
    moves_db = db[game]
    moves_db.drop()

    db_client.close()


def import_all(db_address: str):
    """Import all supported games to the database."""
    
    game_list = ["ggst", "gbvs", "bbcf", "p4u2", "dnfd"]
    for game in game_list:
        if game_list.index(game) != 0:
            print("cooling off...")
            sleep(5)
        import_data(db_address, game)
        print(f"imported {game}.")
    


db_address = "mongodb://10.22.22.29:27017"
import_all(db_address)
