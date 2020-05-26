from copy import deepcopy

from .download import (
    CocktailImagesDownloader,
    CocktailRecipesDownloader,
    CocktailUsefulInfoDownloader,
)


class RawDataset:
    """
    Dataset manages training sets.
    It serves correct formats and can perform additional parsings.
    TODO: add more attributes, split useful info into final list of attributes needed.  # noqa
    TODO: make an interface via setter, getter, modify to allow adding new recipes.
    TODO: maybe split in 2 classes: RawDataset, Dataset.
    """

    def __init__(self):
        self.recipes = None
        self.images = None
        self.useful_info = None

    @property
    def recipes(self):
        return deepcopy(self.recipes)

    @recipes.setter
    def recipes(self, recipes):
        self.recipes = deepcopy(recipes)

    @property
    def images(self):
        return deepcopy(self.images)

    @images.setter
    def images(self, images):
        self.images = deepcopy(images)

    @property
    def useful_info(self):
        return deepcopy(self.useful_info)

    @useful_info.setter
    def useful_info(self, useful_info):
        self.useful_info = deepcopy(useful_info)

    def get_train_set(self):
        self.recipes = CocktailRecipesDownloader().get_recipes()
        self.images = CocktailImagesDownloader().get_images()
        self.useful_info = CocktailUsefulInfoDownloader().get_useful_info()

        # TODO: should be converted to pandas format or any other useful format for training  # noqa
        return [self.recipes, self.images, self.useful_info]

    def dump_train_set(self):
        pass
