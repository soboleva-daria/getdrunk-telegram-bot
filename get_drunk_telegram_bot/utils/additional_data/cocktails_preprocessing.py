import json
from collections import Counter

"""
units = []

with open('cocktails.json') as json_file:
    data = json.load(json_file)
    for cocktail in data:
        for ingredient in cocktail['ingredients']:
            units.append(ingredient['unit'])

print(Counter(units))
"""

oz = 29.5735
default_liqueur_degree = 0.18

with open('alcohol_degree.json') as json_file:
    alcohol_degree = json.load(json_file)

alcoholic_drinks = alcohol_degree.keys()
error_ids = []

with open('cocktails.json') as json_file:
    
    data = json.load(json_file)
    for cocktail in data:

        ingredients = cocktail['ingredients']
        volume, alcohol = 0., 0.

        for component in ingredients:
            if component['name'] == '':
                error_ids.append(cocktail['id'])
                break
            if 'ice cube' in component['name'].lower():
                continue
            if component['unit'] == 'oz':
                volume += float(component['amount'])
            words = component['name'].lower().split()
            for w in words:
                if w in alcoholic_drinks:
                    alcohol += float(component['amount']) * alcohol_degree[w]
                    break
                elif w == 'liqueur':
                    alcohol += float(component['amount']) * default_liqueur_degree

        if len(error_ids) > 0 and error_ids[-1] != cocktail['id']:
            cocktail['ABV'] = round(alcohol / volume, 3)
            cocktail['VOLUME'] = round(volume * oz)

    data = [cocktail for cocktail in data if cocktail['id'] not in error_ids]

    with open('processed_cocktails.json', 'w') as outfile:
        json.dump(data, outfile)
