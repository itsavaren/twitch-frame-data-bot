import requests, json, ffmpeg, streamlink, os
from googletrans import Translator, constants


def translate(full_message):
    words = full_message.lower().split()
    lang = "en"
    if "?" in words[0]:
        if words[1] in constants.LANGUAGES.values():
            for key, val in constants.LANGUAGES.items():
                if words[1] in val:
                    return f"Language code for {val} is {key}"

    if words[0] == "help":
        return f"Format: !translate [destination language/language code(optional)] [phrase].  Example: !translate queso | !translate japanese good morning | !translate fr I see a fish!"
    if words[0] in constants.LANGUAGES.keys():
        lang = words[0]
        words.pop(0)
        query = " ".join(words)
    elif words[0] in constants.LANGUAGES.values():
        for key, value in constants.LANGUAGES.items():
            lang = key if words[0] == value else lang
        words.pop(0)
        query = " ".join(words)
    else:
        query = " ".join(words)

    # init the Google API translator
    translator = Translator()

    # translate text to french text (by default)
    translation = translator.translate(f"{query}", src="auto", dest=f"{lang}")
    if translation.src == "en" and lang == "en":
        translation = translator.translate(f"{query}", src="en", dest="fr")
    if translation.pronunciation:
        return f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest} - {translation.pronunciation})"
    else:
        return f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})"


def identify_song(streamer):

    try:
        os.remove("output.mp3")
    except:
        pass

    with open("./tokens.json") as fp:
        auth_token = json.load(fp)["audd"]

    stream_url = streamlink.streams(f"https://www.twitch.tv/{streamer}")["best"].url
    print(stream_url)

    stream = ffmpeg.input(stream_url, t=10)
    stream = ffmpeg.output(stream, "output.mp3")
    ffmpeg.run(stream)

    data = {
        "api_token": auth_token,
        "return": "apple_music,spotify",
    }
    files = {
        "file": open("output.mp3", "rb"),
    }
    result = requests.post("https://api.audd.io/", data=data, files=files)
    result_json = result.json()

    if result_json["result"]["title"] == "Bring Me Down":
        return f"The song playing now is {result_json['result']['artist']} - {result_json['result']['title']} (SONG 1/5)"

    if result_json["result"]["title"] == "death bed (coffee for your head)":
        return f"The song playing now is {result_json['result']['artist']} - {result_json['result']['title']} (SONG 2/5)"

    if result_json["result"]["title"] == "Dreams (2004 Remaster)":
        return f"The song playing now is {result_json['result']['artist']} - {result_json['result']['title']} (SONG 3/5)"

    return f"The song playing now is {result_json['result']['artist']} - {result_json['result']['title']}"


def wiki_def(raw_name):
    # raw_name = 'cognitive behavior therapy'
    name = raw_name.replace(" ", "%20")
    url = (
        f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&redirects=1&format=json&exintro&explaintext&exsentences=1&titles="
        + name
    )
    source = requests.get(
        url,
        headers={
            "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
        },
    ).json()
    page_dict = source["query"]["pages"]

    for key, value in page_dict.items():
        extract = value["extract"]
        if extract:
            break
    return f"From Wikipedia: {extract}"


def define_word(word):

    with open("./tokens.json") as fp:
        dict_token = json.load(fp)["dict"]

    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word.lower()}?key={dict_token}"

    r = requests.get(url)

    result_json = r.json()

    result_stem = result_json[0]["meta"]["id"].split(":")[0]

    result_part_of_speech = result_json[0]["fl"]

    result_definition = result_json[0]["shortdef"]

    result = f"{result_stem} - {result_part_of_speech}: {result_definition[0]}"

    return result


def bingus_quote():

    return f"Bingus is fucking dead."


def cat_fact():
    url = f"https://catfact.ninja/fact"

    response = requests.get(url).json()

    return response["fact"]
