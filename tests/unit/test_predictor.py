from typing import List
from unittest.mock import create_autospec

import numpy as np
import pytest

from get_drunk_telegram_bot.drinks.dataset import Dataset
from get_drunk_telegram_bot.embeder import TfidfEmbeder
from get_drunk_telegram_bot.model import EmbederModel
from get_drunk_telegram_bot.similarity import CosineSimilarity

_MOCK_EMBEDINGS = {
    '1': np.array([1, 0, 0]),
    '2': np.array([0, 1, 0]),
    '3': np.array([0, 0, 1]),
}


def f(data: List[str]):
    return np.array(list(map(lambda x: _MOCK_EMBEDINGS[x], data)))


@pytest.fixture
def embeder():
    mock = create_autospec(TfidfEmbeder)
    mock.embed.side_effect = f
    return mock


def g(coctail_ids: List[int]):
    return list(map(lambda coctail_id: str(coctail_id + 1), coctail_ids))


@pytest.fixture
def dataset():
    mock = create_autospec(Dataset)
    mock.get_coctails_by_ids.side_effect = g
    mock.get_ingredients.return_value = list(_MOCK_EMBEDINGS.keys())
    return mock


@pytest.mark.parametrize('query', list(_MOCK_EMBEDINGS.keys()))
def test_embeder_model(query, embeder, dataset):
    model = EmbederModel(embeder, dataset, CosineSimilarity(), 0.0)
    prediction = model.predict(query)
    assert [query] == prediction
