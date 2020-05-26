from copy import copy
from io import BytesIO
from typing import Dict, List, Optional

import requests
from lazy import lazy
from PIL import Image


class Cocktail:
    def __init__(
        self,
        name: str,
        characteristics: List[str],
        ingredients: List[Dict[str, str]],
        tools: List[Dict[str, str]],
        recipe: List[str],
        image: Optional[str] = None,
        useful_info: Optional[str] = None,
        abv: Optional[float] = None,
        volume: Optional[float] = None,
    ):
        self._name = name
        self._characteristics = characteristics
        self._ingredients = ingredients
        self._tools = tools
        self._recipe = recipe
        self._image = image
        self._useful_info = useful_info
        self._abv = abv or 0.0
        self._volume = volume or 1.0

    def __repr__(self):
        return f"""
        {self._name}
        characteristics: {self._characteristics}
        ingredients: {self._ingredients}
        tools: {self._tools}
        recipe: {self._recipe}
        abv: {self._abv}
        volume: {self._volume}
        """

    @property
    def name(self):
        return copy(self._name)

    @property
    def ingredients(self):
        return copy(self._ingredients)

    @property
    def abv(self):
        return copy(self._abv)

    @property
    def volume(self):
        return copy(self._volume)

    @property
    def useful_info(self):
        info = []
        if self._useful_info is not None:
            info.append(copy(self._useful_info))
        if self._characteristics is not None:
            info.append(f"\nCharacteristics: {', '.join(self._characteristics)}")
        if len(info) != 0:
            return '\n'.join(info)
        return None

    @ingredients.setter
    def ingredients(self, ingredients):
        self._ingredients = copy(ingredients)

    @lazy
    def image(self):
        if self._image:
            response = requests.get(self._image)
            image = Image.open(BytesIO(response.content))
            return image
        return None

    @property
    def ingredients_str(self):
        return ' '.join(map(lambda x: x['name'].lower(), self._ingredients))

    @property
    def recipe(self) -> str:
        try:
            return '\n'.join([f'{i}. {step}' for i, step in enumerate(self._recipe, 1)])
        except TypeError:
            return ''

    @property
    def pretty_ingredients(self) -> List[str]:
        return [
            f"{ingredient['name']} {ingredient['amount']} {ingredient['unit']}"
            for ingredient in self._ingredients
        ]
