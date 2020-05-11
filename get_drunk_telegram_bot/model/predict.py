from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.drinks.preprocessing import RawDataset

from sklearn.feature_extraction.text import TfidfVectorizer
import sklearn as sk
from typing import List


class BaseModel:
    # BaseModel answers are hardcoded for demo only.
    ORIG_NAME = 'Pina Colada'
    NAME = 'Pina Colada 🍍 🥃'
    INGREDIENTS = ['3 cl rum', '3 cl coconut cream', '9 cl pineapple juice']
    RECIPE = 'Mixed with crushed ice in blender until smooth, then pour into a chilled glass, garnish and serve.  '
    IMG = None
    USEFUL_INFO = 'was officially invented on August 15 1954 by a bartender named Ramón “Monchito” Marrero'
    ABV = 0.1  # alcohol by volume in %
    VOLUME = 70  # in grams

    @staticmethod
    def predict(query):
        cocktail = Cocktail(
            orig_name=BaseModel.ORIG_NAME,
            name=BaseModel.NAME,
            ingredients=BaseModel.INGREDIENTS,
            recipe=BaseModel.RECIPE,
            image=BaseModel.IMG,
            useful_info=BaseModel.USEFUL_INFO,
            abv=BaseModel.ABV,
            volume=BaseModel.VOLUME
        )
        return cocktail


class TFIdfCocktailModel(BaseModel):
    """
    TFIdfCocktailModel performs cocktail recipe search by finding the most similar cocktail recipe TFIDF vector
    for the query.
    """
    def __init__(self, train: RawDataset):
        super().__init__()
        self.train = train
        self.train_vectors = None
        self.trained = False
        self.vectorizer = TfidfVectorizer()

    def normalize(self, matrix):
        # Use any simple normalization technique
        return sk.preprocessing.normalize(matrix, norm='l2', axis=1)

    def vectorize(self, data: List[str], fit=False):
        # Use sklearn.feature_extraction.text.TfidfVectorizer
        if fit:
            self.vectorizer.fit(data)
        return self.vectorizer.transform(data)

    def train_on_recipes(self):
        self.train_vectors = self.normalize(self.vectorize(self.train.get_train_set()[0], True))
        self.trained = True

    def find_matched_cocktail(self, query_vec):
        # Use cosine similarity between train vectors and query_vec -> argmax
        params = {'ingredients': None, 'recipe': None, 'image': None, 'useful_info': None}

        best_cocktail_id = self.train_vectors.dot(query_vec.T).argmax()
        recipes, images, useful_info = self.train.get_train_set()
        params['recipe'] = recipes[best_cocktail_id]
        params['image'] = images[best_cocktail_id]
        params['useful_info'] = useful_info[best_cocktail_id]
        return Cocktail(*params)

    def predict(self, query: str):
        assert self.trained,\
            "Model cannot predict before it is trained, please train the model first by calling train_on_recipes."
        query_vec = self.normalize(self.vectorize([query]))
        return self.find_matched_cocktail(query_vec)


class BertCocktailModel(BaseModel):
    """
    BertCocktailModel performs cocktail recipe search by finding the most similar cocktail recipe using pretrained
    similarity Bert model.
    """
    def __init__(self, model_config_file, model_vocab_file):
        super().__init__()
        self.config = model_config_file
        self.vocab = model_vocab_file
        self.model_weights = None

    def tokenize(self):
        # https://pytorch.org/hub/huggingface_pytorch-transformers/#first-tokenize-the-input
        pass

    def encode(self):
        # https://pytorch.org/hub/huggingface_pytorch-transformers/#using-bertmodel-to-encode-the-input-sentence-in-a-sequence-of-last-layer-hidden-states
        pass

    def load_model_weights(self):
        # Use config, vocab and model_weights of the pretrained model
        pass

    def train_on_recipes(self):
        # instead of training, we can use trained BERT model
        # that can predict similarity between two texts -> argmax
        # for example, train model on similarity GLUE dataset (stsb) and predict it on the cocktails data
        self.model_weights = self.load_model_weights()
        pass

    def find_matched_cocktail(self, query_enc):
        # use this as an example: https://pytorch.org/hub/huggingface_pytorch-transformers/#using-modelforquestionanswering-to-do-question-answering-with-bert
        params = {'ingredients': None, 'recipe': None, 'image': None, 'useful_info': None}
        return Cocktail(*params)

    def predict(self, query):
        query_enc = self.encode(self.tokenize(query))
        return self.find_matched_cocktail(query_enc)