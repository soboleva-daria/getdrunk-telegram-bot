import pathlib
import json

_DATA_PATH = pathlib.Path(__file__).parent

COCTAILS = _DATA_PATH / 'coctails.json'
PROCESSED_COCKTAILS = _DATA_PATH / 'processed_cocktails.json'
ALCOHOL_DEGREE = _DATA_PATH / 'alcohol_degree.json'


def load_data(path: pathlib.Path):
    with path.open(encoding='utf8') as f:
        return json.load(f)
