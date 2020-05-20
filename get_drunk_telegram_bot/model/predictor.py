from typing import List, Optional

from get_drunk_telegram_bot.drinks.dataset import Dataset
from get_drunk_telegram_bot.embeder import IEmbeder
from get_drunk_telegram_bot.model import IModel
from get_drunk_telegram_bot.similarity import CosineSimilarity, ISimilarity
from get_drunk_telegram_bot.drinks.cocktail import Cocktail


class EmbederModel(IModel):
    def __init__(
        self,
        embeder: IEmbeder,
        dataset: Dataset,
        similarity: ISimilarity = CosineSimilarity(),
        min_similarity: Optional[float] = None,
    ):
        self.__embeder = embeder
        self.__dataset = dataset
        self.__similarity = similarity
        self.__min_similarity = min_similarity
        self.__candidate_vectors = self.__embeder.embed(dataset.get_ingredients())

    def predict(self, query: str) -> List[Cocktail]:
        question_embedding = self.__embeder.embed([query])[0]
        similarities, ranks = self.__similarity.rank(question_embedding, self.__candidate_vectors)

        if self.__min_similarity is None:
            coctails_ids = ranks
        else:
            coctails_ids = [rank for rank in ranks if similarities[rank] > self.__min_similarity]

        return self.__dataset.get_coctails_by_ids(coctails_ids)
