import pytest

from get_drunk_telegram_bot.similarity import CosineSimilarity
from tests.chitchat.unit.chatterix.similarity.vector_case import VectorSimilarityTestCase


class CosineSimilarityTest(VectorSimilarityTestCase):
    @property
    def similarity(self):
        return CosineSimilarity()

    @pytest.mark.parametrize(
        ['first', 'second', 'expected_similarity'],
        [([1, 1], [2, 2], 1,), ([1, 2], [2, -1], 0,), ([0, 0], [0, 0], 0,), ([1, 1], [-1, -1], -1,),],
    )
    def test_compute(self, first, second, expected_similarity):
        self.assert_similarity_equal(first, second, expected_similarity)

    @pytest.mark.parametrize(
        ['anchor', 'candidates', 'expected_similarities', 'expected_ranks'],
        [([1, 1], [[0, 0], [-1, -1], [2, 2],], [0, -1, 1], [2, 0, 1],),],
    )
    def test_rank(self, anchor, candidates, expected_similarities, expected_ranks):
        self.assert_ranking_equal(anchor, candidates, expected_similarities, expected_ranks)
