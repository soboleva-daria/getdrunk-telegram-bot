from copy import copy, deepcopy


class Cocktail:

    def __init__(self, ingredients, recipe, image, useful_info):
        self.ingredients = ingredients
        self.recipe = recipe
        self.image = image
        self.useful_info = useful_info

    @property
    def ingredients(self):
        return copy(self.ingredients)

    @ingredients.setter
    def ingredients(self, ingredients):
        self.ingredients = copy(ingredients)

    @property
    def image(self):
        return deepcopy(self.image)

    @image.setter
    def image(self, image):
        self.image = deepcopy(image)