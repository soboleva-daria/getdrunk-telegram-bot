import abc
from typing import List

import numpy as np


class IEmbeder(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def embed(self, data: List[str]) -> np.array:
        """
        Get vectorized data

        Args:
            data: array

        Returns:
            vectors: array
        """
