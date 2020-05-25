from copy import copy, deepcopy


class SimpleDownloader:
    """
    Base class for downloading training data.
    Below you can find specific downloaders for any
    specific part needed for training.
    """

    def __init__(self):
        pass

    def download(self):
        pass


class CocktailRecipesDownloader(SimpleDownloader):
    def __init__(self):
        super().__init__()
        self.recipes = None

    @property
    def recipes(self):
        return deepcopy(self.recipes)

    @recipes.setter
    def recipes(self, recipes):
        self.recipes = deepcopy(recipes)

    def get_recipes(self):
        return self.recipes


class CocktailImagesDownloader(SimpleDownloader):
    def __init__(self):
        super().__init__()
        self.images = None

    @property
    def images(self):
        return deepcopy(self.images)

    @images.setter
    def images(self, images):
        self.images = deepcopy(images)

    def get_images(self):
        return self.images


class CocktailUsefulInfoDownloader(SimpleDownloader):
    # TODO: this class could be reconstructed for specific Downloaders such as:
    # CreatedDatesDownloader, AuthorsDownloader, etc.
    def __init__(self):
        super().__init__()
        self.useful_info = None

    @property
    def useful_info(self):
        return deepcopy(self.useful_info)

    @useful_info.setter
    def useful_info(self, useful_info):
        self.useful_info = deepcopy(useful_info)

    def get_useful_info(self):
        return self.useful_info
