from typing import List

from get_drunk_telegram_bot.embeder import IEmbeder
from get_drunk_telegram_bot.similarity import CosineSimilarity, ISimilarity
from get_drunk_telegram_bot.model import IModel


class EmbederModel(IModel):
    def __init__(
        self,
        embedder: IEmbeder,
        candidate_texts: List[str],
        similarity: ISimilarity = CosineSimilarity(),
        min_similarity: Optional[float] = None,
    ):
        self.__embedder = embedder
        self.__similarity = similarity
        self.__min_similarity = min_similarity
        self.__candidate_vectors = self.__embedder.embed(candidate_texts)

    def predict(query: str) -> List[Cocktail]:
        question_embedding = self.__embedder.embed([query])[0]
        similarities, ranks = self.__similarity.rank(question_embedding, self.__candidate_vectors)

        if self.__min_similarity is None:
            return [ranking_texts[rank] for rank in ranks]

        return [ranking_texts[rank] for rank in ranks if similarities[rank] > self.__min_similarity]
