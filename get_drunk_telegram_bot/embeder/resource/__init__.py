import pathlib

from sklearn.externals import joblib

_ROOT = pathlib.Path(__file__).parent


def load_feature_model():
    return joblib.load(_ROOT / 'feature_model.joblib')
