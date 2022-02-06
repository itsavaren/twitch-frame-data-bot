from googletrans import Translator, constants
from pprint import pprint

def translate(full_message):
    words = full_message.split()
    lang = 'fr'
    if '?' in words[0]:
        if words[1] in constants.LANGUAGES.values():
            for key, val in constants.LANGUAGES.items():
                if words[1] in val:
                    return f'Language code for {val} is {key}'

    if words[0] in constants.LANGUAGES.keys():
        lang = words[0]
        words.pop(0)
        query = ' '.join(words)
    else:
        query = ' '.join(words)

    # init the Google API translator
    translator = Translator()

    # translate text to french text (by default)
    translation = translator.translate(f"{query}", src='auto', dest=f'{lang}')
    if translation.pronunciation:
        return f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest} - {translation.pronunciation})"
    else:
        return f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})"

