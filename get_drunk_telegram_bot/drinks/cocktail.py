from copy import copy, deepcopy
from typing import Dict, List, Optional


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
        return copy(self._useful_info)

    @ingredients.setter
    def ingredients(self, ingredients):
        self._ingredients = copy(ingredients)

    @property
    def image(self):
        return deepcopy(self._image)

    @image.setter
    def image(self, image):
        self._image = deepcopy(image)

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
