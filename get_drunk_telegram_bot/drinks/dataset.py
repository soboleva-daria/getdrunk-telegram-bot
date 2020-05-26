import logging
from typing import Dict, List, Optional

from get_drunk_telegram_bot.data import PROCESSED_COCKTAILS, load_data
from get_drunk_telegram_bot.drinks.cocktail import Cocktail

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class Dataset:
    def __init__(self):
        coctails_info = map(
            self.__preprocess_coctail_info, load_data(PROCESSED_COCKTAILS)
        )
        self.__coctails = {
            i: Cocktail(**coctail_info) for i, coctail_info in enumerate(coctails_info)
        }

    def __len__(self):
        return len(self.__coctails)

    def __preprocess_coctail_info(self, coctail_info: Dict) -> Dict:
        return {k.lower(): i for k, i in coctail_info.items() if k != 'id'}

    def get_ingredients(self) -> List[str]:
        return [coctail.ingredients_str for coctail in self.__coctails.values()]

    def get_names_and_ingredients(self) -> List[str]:
        return [(coctail.name, coctail.ingredients_str) for coctail in self.__coctails.values()]

    def get_coctail_by_id(self, coctail_id: int) -> Optional[Cocktail]:
        try:
            return self.__coctails[coctail_id]
        except KeyError:
            logging.warning(f'Tried to get non existing coctail: {coctail_id}')

    def get_coctails_by_ids(self, coctail_ids: List[int]) -> List[Cocktail]:
        coctails = [self.get_coctail_by_id(i) for i in coctail_ids]
        return coctails
