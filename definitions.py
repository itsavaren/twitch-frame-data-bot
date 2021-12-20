import json
import requests



def define_word(word):

    app_id  = "131f4a06"
    app_key  = "2d63881f00805ec6588e4366d0a45c03"
    endpoint = "entries"
    language_code = "en-us"
    fields = 'definitions'


    word_id = word


    url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()

    r = requests.get(url, headers = {"app_id": app_id, "app_key": app_key, "fields": fields})

    print("code {}\n".format(r.status_code))

    definition = r.json()

    results = definition['results']

    results = results[0]

    results = results['lexicalEntries']

    results = results[0]

    results = results['entries']

    results = results[0]

    results = results['senses']

    results = results[0]

    results = results['definitions']

    result = results[0]

    return result