from typing import Tuple

import numpy as np

from get_drunk_telegram_bot.similarity import ISimilarity


class CosineSimilarity(ISimilarity):
    def compute(self, first: np.array, second: np.array) -> float:
        product = first.dot(second)
        if product == 0:
            return 0

        return product / (np.linalg.norm(first) * np.linalg.norm(second))

    def rank(self, anchor: np.array, candidates: np.array) -> Tuple[np.array, np.array]:
        products = np.inner(anchor, candidates)

        norms = np.linalg.norm(anchor) * np.linalg.norm(candidates, axis=1)
        norms[norms == 0] = 1

        similarities = products / norms
        return similarities, np.argsort(-similarities)
