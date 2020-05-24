from typing import Sequence

import numpy as np
import pytest

from get_drunk_telegram_bot.similarity.cosine import CosineSimilarity


class CosineSimilarityTest:
    @property
    def similarity(self):
        return CosineSimilarity()

    def assert_similarity_equal(
        self,
        first: Sequence[float],
        second: Sequence[float],
        expected_similarity: float,
    ):
        actual_similarity = self.similarity.compute(np.array(first), np.array(second))

        np.testing.assert_almost_equal(expected_similarity, actual_similarity)

    def assert_ranking_equal(
        self, anchor, candidates, expected_similarities, expected_ranks
    ):
        actual_similarities, actual_ranks = self.similarity.rank(anchor, candidates)

        np.testing.assert_array_almost_equal(expected_similarities, actual_similarities)
        np.testing.assert_array_equal(expected_ranks, actual_ranks)

    @pytest.mark.parametrize(
        ['first', 'second', 'expected_similarity'],
        [
            ([1, 1], [2, 2], 1),
            ([1, 2], [2, -1], 0),
            ([0, 0], [0, 0], 0),
            ([1, 1], [-1, -1], -1),
        ],
    )
    def test_compute(self, first, second, expected_similarity):
        self.assert_similarity_equal(first, second, expected_similarity)

    @pytest.mark.parametrize(
        ['anchor', 'candidates', 'expected_similarities', 'expected_ranks'],
        [([1, 1], [[0, 0], [-1, -1], [2, 2]], [0, -1, 1], [2, 0, 1])],
    )
    def test_rank(self, anchor, candidates, expected_similarities, expected_ranks):
        self.assert_ranking_equal(
            anchor, candidates, expected_similarities, expected_ranks
        )
