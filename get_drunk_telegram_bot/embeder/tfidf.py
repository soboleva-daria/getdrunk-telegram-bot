from typing import List

from get_drunk_telegram_bot.embeder import IEmbeder
from get_drunk_telegram_bot.resource import load_tfidf_model


class TfidfEmbeder(IEmbeder):
    def __init__(self):
        self.__vectorizer = load_tfidf_model()

    def embed(self, data: List[str]) -> np.array:
        return self.vectorizer.transform(data)
