from typing import List

from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.model import IModel


class BaseModel(IModel):
    # BaseModel answers are hardcoded for demo only.
    NAME = 'Pina Colada 🍍 🥃'
    CHARACTERISTICS = ['sweet']
    INGREDIENTS = [
        {'name': 'Rum', 'amount': '3', 'unit': 'cl'},
        {'name': 'Coconut cream', 'amount': '3', 'unit': 'cl'},
        {'name': 'Pineapple juice', 'amount': '9', 'unit': 'cl'},
    ]
    TOOLS =  [
        {'name': 'Cocktail glass', 'amount': '1', 'unit': 'piece'},
        {'name': 'Shaker', 'amount': '1', 'unit': 'piece'},
    ]
    RECIPE = [
        'Mixed with crushed ice in blender until smooth',
        'pour into a chilled glass, garnish and serve.'
    ]
    IMG = None
    USEFUL_INFO = (
        'was officially invented on August 15 1954 by a bartender '
        'named Ramón “Monchito” Marrero'
    )
    ABV = 0.1  # alcohol by volume in %
    VOLUME = 70  # in grams

    @staticmethod
    def predict(query: str) -> List[Cocktail]:
        cocktail = Cocktail(
            name=BaseModel.NAME,
            characteristics=BaseModel.CHARACTERISTICS,
            ingredients=BaseModel.INGREDIENTS,
            tools=BaseModel.TOOLS,
            recipe=BaseModel.RECIPE,
            image=BaseModel.IMG,
            useful_info=BaseModel.USEFUL_INFO,
            abv=BaseModel.ABV,
            volume=BaseModel.VOLUME
        )
        return [cocktail]
