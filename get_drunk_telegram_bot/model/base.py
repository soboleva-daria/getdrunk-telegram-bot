from typing import List

from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.model import IModel


class BaseModel(IModel):
    # BaseModel answers are hardcoded for demo only.
    ORIG_NAME = 'Pina Colada'
    NAME = 'Pina Colada 🍍 🥃'
    INGREDIENTS = ['3 cl rum', '3 cl coconut cream', '9 cl pineapple juice']
    RECIPE = (
        'Mixed with crushed ice in blender until smooth, then pour into a '
        'chilled glass, garnish and serve.'
    )
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
            orig_name=BaseModel.ORIG_NAME,
            name=BaseModel.NAME,
            ingredients=BaseModel.INGREDIENTS,
            recipe=BaseModel.RECIPE,
            image=BaseModel.IMG,
            useful_info=BaseModel.USEFUL_INFO,
            abv=BaseModel.ABV,
            volume=BaseModel.VOLUME
        )
        return [cocktail]
