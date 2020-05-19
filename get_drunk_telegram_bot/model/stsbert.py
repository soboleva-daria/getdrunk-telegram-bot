from typing import List

import numpy as np
from semantic_text_similarity.models import WebBertSimilarity

from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.drinks.preprocessing import RawDataset
from get_drunk_telegram_bot.model import IModel


class STSBertCocktailModel(IModel):
    """
    STSBertCocktailModel performs cocktail recipe search by finding
    the most similar cocktail recipe using pretrained similarity Bert model.
    """
    def __init__(self, train: RawDataset):
        super().__init__()
        self.train = train
        self.model = WebBertSimilarity(device='cpu', batch_size=10)

    def find_one_best_cocktail(self, query: str, data: List):
        """
        data: List of n best cocktail's recipes
        """
        predictions = self.model.predict([(recipe, query) for recipe in data])
        return np.array(predictions).argmax()

    def predict(query: str) -> List[Cocktail]:
        params = {'ingredients': None, 'recipe': None, 'image': None,
                  'useful_info': None}
        return Cocktail(*params)
