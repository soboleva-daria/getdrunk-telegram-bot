import abc
from typing import List

from get_drunk_telegram_bot.drinks.cocktail import Cocktail


class IModel(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def predict(query: str) -> List[Cocktail]:
        """
        Find closest coctails by query

        Args:
            query: client ingredients, str

        Returns:
            coctals: closest coctails, array
        """
