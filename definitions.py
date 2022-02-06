import requests

def define_word(word):

    with open('dict_token.txt') as fp:
        dict_token = fp.read()


    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word.lower()}?key={dict_token}"

    r = requests.get(url)

    result_json = r.json()

    result_stem = result_json[0]['meta']['id'].split(':')[0]

    result_part_of_speech = result_json[0]['fl']

    result_definition = result_json[0]['shortdef']

    result = f'{result_stem} - {result_part_of_speech}: {result_definition[0]}'


    return result