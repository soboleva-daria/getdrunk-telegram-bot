from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.drinks.preprocessing import RawDataset

from sklearn.feature_extraction.text import TfidfVectorizer
import sklearn as sk
import numpy as np
import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel
from semantic_text_similarity.models import WebBertSimilarity
from typing import List


class BaseModel:
    # BaseModel answers are hardcoded for demo only.
    ORIG_NAME = 'Pina Colada'
    NAME = 'Pina Colada 🍍 🥃'
    INGREDIENTS = ['3 cl rum', '3 cl coconut cream', '9 cl pineapple juice']
    RECIPE = (
        'Mixed with crushed ice in blender until smooth, then pour into a '
        'chilled glass, garnish and serve.'
    )
    IMG = None
    USEFUL_INFO = (
        'was officially invented on August 15 1954 by a bartender '
        'named Ramón “Monchito” Marrero'
    )
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
    TFIdfCocktailModel performs cocktail recipe search by finding the most
    similar cocktail recipe TF-IDF vector for the query.
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
        self.train_vectors = self.normalize(self.vectorize(
            self.train.get_train_set()[0], True))
        self.trained = True

    def find_matched_cocktail(self, query_vec):
        # Use cosine similarity between train vectors and query_vec -> argmax
        params = {
            'ingredients': None, 'recipe': None,
            'image': None, 'useful_info': None
        }

        best_cocktail_id = self.train_vectors.dot(query_vec.T).argmax()
        recipes, images, useful_info = self.train.get_train_set()
        params['recipe'] = recipes[best_cocktail_id]
        params['image'] = images[best_cocktail_id]
        params['useful_info'] = useful_info[best_cocktail_id]
        return Cocktail(*params)

    def predict(self, query: str):
        assert self.trained, (
            "Model cannot predict before it is trained, please train the\
            model first by calling train_on_recipes."
        )
        query_vec = self.normalize(self.vectorize([query]))
        return self.find_matched_cocktail(query_vec)


class BertCocktailModel(BaseModel):
    """
    BertCocktailModel performs cocktail recipe search by finding the most
    similar cocktail recipe using Bert model.
    """
    def __init__(self, train: RawDataset, model_name='bert-base-uncased'):
        super().__init__()
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.max_sequence_len = 256
        self.train = train
        self.train_vectors = None
        self.trained = False

    def tokenize(self, text: str):
        tokenized_text = self.tokenizer.tokenize(text)
        return ['CLS'] + tokenized_text + ['SEP'] + \
               ['PAD'] * (self.max_sequence_len - len(tokenized_text) - 2)

    def encode(self, tokenized_text: List):
        return self.tokenizer.convert_tokens_to_ids(tokenized_text)

    def train_on_recipes(self, batch_size=32):

        train_texts = self.train.get_train_set()[0]
        batches = []

        for i in range(0, len(train_texts), batch_size):
            tokens_tensor = torch.tensor([
                            self.encode(self.tokenize(text))
                            for text in train_texts[i:i + batch_size]
                            ])
            encoded_layers, _ = self.model(tokens_tensor)
            batches.append(encoded_layers[-1][:, 0, :])

        self.train_vectors = torch.cat(batches)
        self.trained = True

    def find_matched_cocktail(self, query_enc):
        params = {'ingredients': None, 'recipe': None,
                  'image': None, 'useful_info': None}

        best_cocktail_id = torch.mm(
                   self.train_vectors, query_enc.T).argmax().item()
        recipes, images, useful_info = self.train.get_train_set()
        params['recipe'] = recipes[best_cocktail_id]
        params['image'] = images[best_cocktail_id]
        params['useful_info'] = useful_info[best_cocktail_id]
        return Cocktail(*params)

    def predict(self, query):
        assert self.trained, \
            "Model cannot predict before it is trained\
             please train the model first by calling train_on_recipes."
        query_enc = self.encode(self.tokenize(query))
        return self.find_matched_cocktail(query_enc)


class STSBertCocktailModel(BaseModel):
    """
    STSBertCocktailModel performs cocktail recipe search by finding
    the most similar cocktail recipe using pretrained similarity Bert model.
    """
    def __init__(self, train: RawDataset):
        super().__init__()
        self.train = train
        self.model = WebBertSimilarity(device='cpu', batch_size=10)

    def find_one_best_cocktail(self, query: str, data: List):
        """
        data: List of n best cocktail's recipes
        """
        predictions = self.model.predict([(recipe, query) for recipe in data])
        return np.array(predictions).argmax()

    def predict(self, query):
        params = {'ingredients': None, 'recipe': None, 'image': None,
                  'useful_info': None}
        return Cocktail(*params)
