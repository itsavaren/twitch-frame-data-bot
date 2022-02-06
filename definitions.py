import requests


def define_word(word):

    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + word.lower()

    r = requests.get(url)

    result_json = r.json()

    result_part_of_speech = result_json[0]['meanings'][0]['partOfSpeech']

    result_definition = result_json[0]['meanings'][0]['definitions'][0]['definition']

    result = f'{word} - {result_part_of_speech}: {result_definition}'


    return result