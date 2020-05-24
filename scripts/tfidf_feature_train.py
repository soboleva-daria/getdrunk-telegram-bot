import argparse
import logging
import pickle
from pathlib import Path

from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

from get_drunk_telegram_bot.drinks.dataset import Dataset

_DEFAULT_MODEL_OUT = Path(
    '../get_drunk_telegram_bot/embeder/resource/feature_model.joblib'
)


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-dd', '--data_dir', type=Path, default=_DEFAULT_MODEL_OUT)


def train():
    args = parser.parse_args()
    dataset = Dataset()
    data = dataset.get_ingredients()
    features = FeatureUnion(
        [
            ('words', TfidfVectorizer(min_df=2, stop_words=['ice', 'cubes'])),
            ('chars', TfidfVectorizer(min_df=20, analyzer='char', ngram_range=(2, 5))),
        ]
    )
    features.fit(data)
    joblib.dump(features, args.data_dir, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    train()
