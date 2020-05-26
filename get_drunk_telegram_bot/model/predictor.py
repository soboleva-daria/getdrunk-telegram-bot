from typing import List, Optional

from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.drinks.dataset import Dataset
from get_drunk_telegram_bot.embeder import IEmbeder
from get_drunk_telegram_bot.model import IModel
from get_drunk_telegram_bot.similarity import CosineSimilarity, ISimilarity


class EmbederModel(IModel):
    def __init__(
        self,
        embeder: IEmbeder,
        dataset: Dataset,
        similarity: ISimilarity = CosineSimilarity(),
        max_similarity: Optional[float] = None,
        min_similarity: Optional[float] = None,
    ):
        self.__embeder = embeder
        self.__dataset = dataset
        self.__similarity = similarity
        self.__max_similarity = max_similarity
        self.__min_similarity = min_similarity
        self.__candidate_vectors = self.__embeder.embed(dataset.get_ingredients())

    def predict(self, query: str, ignore_max_similarity=False) -> List[Cocktail]:
        question_embedding = self.__embeder.embed([query])[0]
        similarities, ranks = self.__similarity.rank(
            question_embedding, self.__candidate_vectors
        )

        coctails_ids = []

        if self.__max_similarity is not None and not ignore_max_similarity:
            coctails_ids = [
                rank for rank in ranks if similarities[rank] > self.__max_similarity
            ]
        if len(coctails_ids) == 0 and self.__min_similarity is not None:
            coctails_ids = [
                rank for rank in ranks if similarities[rank] > self.__min_similarity
            ]
        if len(coctails_ids) == 0 and self.__max_similarity is None and self.__min_similarity is None:
            coctails_ids = ranks

        return self.__dataset.get_coctails_by_ids(coctails_ids)
