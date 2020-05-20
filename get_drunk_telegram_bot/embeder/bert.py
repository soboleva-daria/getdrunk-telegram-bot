from typing import List

import numpy as np
import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel

from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.drinks.preprocessing import RawDataset
from get_drunk_telegram_bot.embeder import IEmbeder


class BertEmbeder(IEmbeder):
    """
    BertCocktailModel performs cocktail recipe search by finding the most
    similar cocktail recipe using Bert model.
    """
    def __init__(
        self,
        model_name='bert-base-uncased',
        batch_size: int = 32,
    ):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.max_sequence_len = 256
        self.batch_size = 32

    def tokenize(self, text: str):
        tokenized_text = self.tokenizer.tokenize(text)
        return ['CLS'] + tokenized_text + ['SEP'] + \
               ['PAD'] * (self.max_sequence_len - len(tokenized_text) - 2)

    def encode(self, tokenized_text: List):
        return self.tokenizer.convert_tokens_to_ids(tokenized_text)

    def embed(self, data: List[str]) -> np.array:
        batches = []

        for i in range(0, len(data), self.batch_size):
            tokens_tensor = torch.tensor([
                            self.encode(self.tokenize(text))
                            for text in data[i:i + batch_size]
                            ])
            encoded_layers, _ = self.model(tokens_tensor)
            batches.append(encoded_layers[-1][:, 0, :])

        return torch.cat(batches).numpy()
