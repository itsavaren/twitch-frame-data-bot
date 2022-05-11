import json, re
from pymongo import MongoClient, ASCENDING, DESCENDING
from pprint import *


def char_select(search_term: str):
    """Search for and select a character or characters from the roster_list.json file."""
    with open("./db/roster_list.json", "r") as fp:
        roster_list = json.load(fp)
    results = {}
    for key, value in roster_list.items():
        matches = [match for match in value if search_term == match]
        if not matches:
            matches = [
                match for match in value if re.findall(f"^{search_term}.*", match)
            ]
        if matches:
            results[key] = matches
    if results:
        return results
    else:
        return None


def get_headers(db_client: MongoClient, type: str, selected_game: str):
    """Return the keys of a collection."""
    return (
        db_client[type][selected_game]
        .aggregate(
            [
                {"$project": {"arrayofkeyvalue": {"$objectToArray": "$$ROOT"}}},
                {"$unwind": "$arrayofkeyvalue"},
                {
                    "$group": {
                        "_id": "null",
                        "allkeys": {"$addToSet": "$arrayofkeyvalue.k"},
                    }
                },
            ]
        )
        .next()["allkeys"]
    )


def update_note(
    db_client: MongoClient,
    streamer: str,
    game: str,
    character: str,
    move: str,
    note: str,
):
    """Update the notes column of a given move in a given game's framedata sqlite database file."""
    db = db_client["moves"][game]
    db.update_one(
        {
            "chara": character,
            "input": move,
        },
        {"$set": {f"custom_note.{streamer}": note}},
    )


def get_note(
    db_client: MongoClient,
    streamer: str,
    game: str,
    character: str,
    move: str,
):
    db = db_client["moves"][game]
    result = db.find_one(
        {
            "chara": character,
            "input": move,
        },
    )
    return result["custom_note"][streamer]


def get_plus(db_client: MongoClient, game: str, character: str):
    """Get the 5 most plus on block moves by plus frames for a given character."""
    db = db_client["moves"][game]
    ordered = list(
        db.find(
            {
                "$and": [
                    {"chara": character},
                    {"onblock": {"$exists": True}},
                    {"onblock": {"$gt": 0}},
                ]
            }
        ).sort("onblock", DESCENDING)
    )
    out_string = f"{character}'s {len(ordered)} plus-est moves are: " + " | ".join(
        [f"{k['input']} - {k['onblock']}f" for k in ordered if "startup" in k.keys()][
            :5
        ]
    )

    return out_string


def get_fastest(db_client: MongoClient, game: str, character: str) -> str:
    """Get the 5 fastest normal moves by startup frames for a given character."""
    db = db_client["moves"][game]
    ordered = list(
        db.find(
            {
                "$and": [
                    {"chara": character},
                    {"startup": {"$exists": True}},
                    {"startup": {"$type": "int"}},
                ]
            }
        )
        .where("!this.input.includes('6d') && !this.input.includes('j.')")
        .sort("startup", ASCENDING)
    )
    out_string = f"{character}'s 5 fastest moves are: " + " | ".join(
        [f"{k['input']} - {k['startup']}f" for k in ordered if "startup" in k.keys()][
            :5
        ]
    )
    return out_string


def get_slowest(db_client: MongoClient, game: str, character: str):
    """Get the 5 slowest moves by startup frames for a given character."""
    db = db_client["moves"][game]
    ordered = list(
        db.find(
            {
                "$and": [
                    {"chara": character},
                    {"startup": {"$exists": True}},
                    {"startup": {"$type": "int"}},
                ]
            }
        )
        .where("!this.input.includes('6d') && !this.input.includes('j.')")
        .sort("startup", DESCENDING)
    )
    out_string = f"{character}'s 5 slowest moves are: " + " | ".join(
        [f"{k['input']} - {k['startup']}f" for k in ordered if "startup" in k.keys()][
            :5
        ]
    )
    return out_string


def get_supers(db_client: MongoClient, game: str, character: str):
    """Get the super moves  for a given character."""
    db = db_client["moves"][game]
    ordered = list(db.find({"$and": [{"chara": character}, {"type": "super"}]}))
    out_string = f"{character}'s super moves are: " + " | ".join(
        [f"{k['name']} - {k['input']}f" for k in ordered]
    )
    return out_string


def get_move_data(
    db_client: MongoClient, game: str, character: str, move_input: str, detail=None
):
    """Get the move data for a given input or name.  Returns either a set short set of properties, specific property, or all properties based on query."""

    moves_db = db_client["moves"][game]

    moves_found = list(
        moves_db.find({"$and": [{"chara": character}, {"input": move_input}]})
    )
    selected_by = "input"

    if not moves_found:
        moves_found = list(
            moves_db.find(
                {
                    "$and": [
                        {"chara": character},
                        {"input": {"$regex": f"{move_input}.*"}},
                    ]
                }
            )
        )
        selected_by = "input"
    if not moves_found:
        moves_found = list(
            moves_db.find(
                {
                    "$and": [
                        {"chara": character},
                        {"name": {"$regex": f".*{move_input.replace(' ', '*.')}.*"}},
                    ]
                }
            )
        )
        selected_by = "name"
    if not moves_found:
        return "No matching result for move input or name."

    if len(moves_found) > 4:
        return str(
            f"More than 4 moves were found by {selected_by} for {move_input}. Be more specific"
        )
    if len(moves_found) > 1 and selected_by == "input":
        return str(
            f"Multiple moves found by input: {', '.join([move_data['input'] for move_data in moves_found])}"
        )
    elif len(moves_found) > 1 and selected_by == "name":
        return str(
            f"Multiple moves found by name: {', '.join([move_data['name']+' - '+move_data['input'] for move_data in moves_found])}"
        )
    else:
        move_data = moves_found[0]

    if detail == None:
        final_output = ""
        for move_stat in ["chara", "name", "input"]:
            try:
                final_output += f"{move_data[move_stat]} "
            except Exception:
                pass
        final_output += "-"
        for move_stat in ["startup", "onblock", "onhit", "recovery"]:
            try:
                final_output += f" {move_stat}: {move_data[move_stat]},"
            except Exception:
                pass
        return final_output[:-1]

    if "detail" in detail:
        return ", ".join(
            [
                f"{keys}: {values}"
                for (keys, values) in move_data.items()
                if keys != "_id"
            ]
        )
    else:
        try:
            return f"{move_data['chara']} {move_data[selected_by]} - {detail}: {move_data[detail]}"
        except:
            return f"No '{detail}' stat found for {move_data['chara']} {move_data[selected_by]}"


def get_char_data(
    db_client: MongoClient, game: str, character: str, detail: str = None
):
    """Get the character data for a given character.  Returns either a set short set of properties, specific property, or all properties based on query."""

    chars_db = db_client["chars"][game]

    char_dict = list(chars_db.find({"name": character}))[0]

    if detail == None:
        if game == "ggst":
            return str(
                f"{char_dict['name']}  - defense: {char_dict['defense']}, guts: {char_dict['guts']}, weight: {char_dict['weight']}, backdash: {char_dict['backdash']}"
            )
        elif game == "p4u2":
            return str(
                f"{char_dict['name']}  - health: {char_dict['health']}, personacards: {char_dict['personacards']}, backdash: {char_dict['backdash']}"
            )
        elif game == "gbvs":
            return str(
                f"{char_dict['name']}  - defense: {char_dict['defense']}, guts: {char_dict['guts']}, weight: {char_dict['weight']}, backdash: {char_dict['backdash']}"
            )
    if "detail" in detail:
        return ", ".join(
            [
                f"{keys}: {values}"
                for (keys, values) in char_dict.items()
                if keys != "_id"
            ]
        )
    else:
        return str(f"{char_dict['name']} {detail}: {char_dict[detail]}")


def parse_move(db_client: MongoClient, streamer: str, full_message: str):
    """Parse the query passed from a twitch user to validate character/game, input/move name, and selected properties, or other functions."""

    games = []
    words = full_message.lower().split()

    if words[0] in ["ggst", "bbcf", "p4u2", "dnfd", "gbvs"]:
        games.append(words.pop(0))

    first_two = char_select(" ".join(words[:2]))
    first_word = char_select(words[0])

    if first_two:
        characters = first_two
        words = words[2:]
    elif first_word:
        characters = first_word
        words = words[1:]
    else:
        return "Character not found."

    if not games:
        for key in characters.keys():
            games.append(key)

    if len(games) == 1:
        selected_game = games[0]
        character_list = characters[selected_game]
        if len(character_list) > 1:
            return f"Multiple characters found in {selected_game}: {', '.join(character_list)}"
        else:
            character = character_list[0]
    else:
        return f"Multiple games found, specify game {games} example: '!fd ggst anji 5h'"

    move_headers = get_headers(db_client, "moves", selected_game)
    char_headers = get_headers(db_client, "chars", selected_game)

    if words[-1] in move_headers or words[-1] in char_headers or "detail" in words[-1]:
        specifier = words.pop()
    else:
        specifier = None

    if words[0] == "info":
        return get_char_data(db_client, selected_game, character, specifier)

    if "fastest" in words:
        return get_fastest(db_client, selected_game, character)
    if "slowest" in words:
        return get_slowest(db_client, selected_game, character)
    if "super" in words or "supers" in words:
        return get_supers(db_client, selected_game, character)
    if "plus" in words:
        return get_plus(db_client, selected_game, character)

    if words[0] == "!add":
        update_note(
            db_client, streamer, selected_game, character, words[1], " ".join(words[2:])
        )
        return f"{character} {words[1]} notes updated."

    move_input_list = db_client["moves"][selected_game].distinct("input")
    if words[0] in move_input_list:
        query = words.pop(0)
    else:
        query = ".*".join(words)

    result = get_move_data(db_client, selected_game, character, query, specifier)

    return result
