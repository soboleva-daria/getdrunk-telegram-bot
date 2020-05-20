from copy import copy, deepcopy
from typing import Dict, List, Optional


class Cocktail:
    def __init__(self,
                 name: str,
                 characteristics: List[str],
                 ingredients: List[Dict[str, str]],
                 tools: List[Dict[str, str]],
                 recipe: List[str],
                 image: Optional[str] = None,
                 useful_info: Optional[str] = None,
                 abv: Optional[float] = None,
                 volume: Optional[float] = None):
        self.__name = name
        self.__characteristics = characteristics
        self.__ingredients = ingredients
        self.__tools = tools
        self.__recipe = recipe
        self.__image = image
        self.__useful_info = useful_info
        self.__abv = abv
        self.__volume = volume

    def __repr__(self):
        return f"""
        {self.__name}
        characteristics: {self.__characteristics}
        ingredients: {self.__ingredients}
        tools: {self.__tools}
        recipe: {self.__recipe}
        abv: {self.__abv}
        volume: {self.__volume}
        """

    @property
    def name(self):
        return copy(self.__name)

    @property
    def ingredients(self):
        return copy(self.__ingredients)

    @ingredients.setter
    def ingredients(self, ingredients):
        self.__ingredients = copy(ingredients)

    @property
    def image(self):
        return deepcopy(self.__image)

    @image.setter
    def image(self, image):
        self.__image = deepcopy(image)

    @property
    def ingredients_str(self):
        return ' '.join(map(lambda x: x['name'].lower(), self.__ingredients))

    @property
    def recipe(self) -> str:
        return '\n'.join([f'{i}. {step}' for i, step in enumerate(self.__recipe, 1)])

    @property
    def pretty_ingredients(self) -> List[str]:
        return [
            f"{ingredient['name']} {ingredient['amount']} {ingredient['unit']}"
            for ingredient in self.__ingredients
        ]
