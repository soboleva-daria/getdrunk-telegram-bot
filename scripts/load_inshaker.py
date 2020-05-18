import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

from bs4 import BeautifulSoup

URL = 'https://us.inshaker.com'

NAME_PATTERN = re.compile(r'<a class="common-good-info".*>(.*)<div class="good-count">')
AMOUNT_PATTERN = re.compile(r'<amount>(.*)</amount>')
UNIT_PATTERN = re.compile(r'<unit>(.*)</unit>')

GLOBAL_LIMIT = 3000


def get_name(soup: BeautifulSoup) -> str:
    return soup.select('h1.common-name')[0].get_text()


def get_characteristics(soup: BeautifulSoup) -> Iterable[str]:
    return list(map(lambda x: x.get_text().strip(), soup.select('li.item')))


def get_ingredients(soup: BeautifulSoup) -> Iterable[Dict[str, Any]]:
    ingredients = []
    ingredients_table = soup.select('dl.ingredients')[0]
    ingredients_info = ingredients_table.select('a.common-good-info')
    for ingredient_info in ingredients_info:
        ingredient = {}
        ingredient['name'] = re.search(NAME_PATTERN, str(ingredient_info)).group(1)
        ingredient['amount'] = re.search(AMOUNT_PATTERN, str(ingredient_info)).group(1)
        ingredient['unit'] = re.search(UNIT_PATTERN, str(ingredient_info)).group(1)
        ingredients.append(ingredient)
    return ingredients


def get_tools(soup: BeautifulSoup) -> Iterable[Dict[str, Any]]:
    tools = []
    tools_info = soup.select('dl.tools')[0].select('a.common-good-info')
    for tool_info in tools_info:
        tool = {}
        tool['name'] = re.search(NAME_PATTERN, str(tool_info)).group(1)
        tool['amount'] = re.search(AMOUNT_PATTERN, str(tool_info)).group(1)
        tool['unit'] = re.search(UNIT_PATTERN, str(tool_info)).group(1)
        tools.append(tool)
    return tools


def get_recipe(soup: BeautifulSoup) -> Iterable[str]:
    return list(
        map(lambda x: x.get_text().strip(), soup.select('ul.steps')[0].select('li'))
    )


def get_image(soup: BeautifulSoup) -> str:
    return URL + soup.select('img.image')[0]['src']


def get_coctail_info(coctail_id: int):
    cocktail_url = URL + f'/cocktails/{coctail_id}'
    html = urlopen(cocktail_url)
    soup = BeautifulSoup(html, 'html.parser')
    coctail_info = {}
    coctail_info['id'] = coctail_id
    coctail_info['name'] = get_name(soup)
    coctail_info['characteristics'] = get_characteristics(soup)
    coctail_info['ingredients'] = get_ingredients(soup)
    coctail_info['tools'] = get_tools(soup)
    coctail_info['recipe'] = get_recipe(soup)
    coctail_info['image'] = get_image(soup)
    return coctail_info


def load_coctails_data(num_limit: Optional[int] = None):
    coctails = []
    for i in range(1, GLOBAL_LIMIT + 1):
        try:
            coctail_info = get_coctail_info(i)
            coctails.append(coctail_info)
        except HTTPError:
            continue
        if len(coctails) == num_limit:
            break
    return coctails


parser = argparse.ArgumentParser()
parser.add_argument('-dd', '--data_dir', type=Path, default='../data/coctails.json')
parser.add_argument('-num', '--num_limit', type=int, default=None)

if __name__ == '__main__':
    args = parser.parse_args()
    coctails = load_coctails_data(args.num_limit)
    with open(args.data_dir, 'w+') as f:
        json.dump(coctails, f, ensure_ascii=False)
