import pathlib

from sklearn.externals import joblib

_ROOT = pathlib.Path(__file__).parent


def load_tfidf_model():
    return joblib.load(_ROOT / 'tfidf.joblib')
