import json
from copy import deepcopy

from get_drunk_telegram_bot.drinks.cocktail import Cocktail


def decode_json(dct):
    if "__cocktail__" in dct:
        dct.pop("__cocktail__", None)
        return Cocktail(**dct)
    elif isinstance(dct, dict):
        result = {}
        for key, value in dct.items():
            if key.isdigit():
                result[int(key)] = value
            else:
                result[key] = value
        return result

    return dct


def encode_json(obj):
    if isinstance(obj, Cocktail):
        dct = deepcopy(obj.__dict__)

        dct['__cocktail__'] = True
        for key, value in obj.__dict__.items():
            if key.startswith('_'):
                dct.pop(key, None)
                dct[key.replace('_', '', 1)] = deepcopy(value)
        return dct
    elif isinstance(obj, map):
        return list(obj)
    else:
        return json.JSONEncoder().default(obj)
      
def normalize_text(text):
    """
    Provides basic normalization by removing trailing spaces from text.

    :param text: str, text to send to user.
    """
    return '\n'.join([line.strip() for line in text.split('\n')])
