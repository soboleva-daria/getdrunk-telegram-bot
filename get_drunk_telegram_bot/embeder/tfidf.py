from typing import List

import numpy as np

from get_drunk_telegram_bot.embeder import IEmbeder
from get_drunk_telegram_bot.embeder.resource import load_feature_model


class TfidfEmbeder(IEmbeder):
    def __init__(self):
        self.__vectorizer = load_feature_model()

    def embed(self, data: List[str]) -> np.array:
        return self.__vectorizer.transform(data).toarray()
