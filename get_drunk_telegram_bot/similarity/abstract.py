import abc
from typing import Tuple

import numpy as np


class ISimilarity(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def compute(self, first: np.array, second: np.array) -> float:
        """
        Finds simularity between two vectors
        """

    @abc.abstractmethod
    def rank(self, anchor: np.array, candidates: np.array) -> Tuple[np.array, np.array]:
        """
        Ranks candidate vectors taking in the account anchor vector

        Args:
            anchor: array, [vector_size]
            candidates: array, [candidate_count, vector_size]

        Returns:
            similarities: array, [candidate_count]
            ranks: array, [candidate_count]
        """
