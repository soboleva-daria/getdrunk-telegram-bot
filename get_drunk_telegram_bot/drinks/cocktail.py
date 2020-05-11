from copy import copy, deepcopy


class Cocktail:

    def __init__(self, orig_name, name, ingredients, recipe, image, useful_info, abv, volume):
        self.orig_name = orig_name
        self.name = name
        self._ingredients = ingredients
        self.recipe = recipe
        self._image = image
        self.useful_info = useful_info
        self.abv = abv
        self.volume = volume

    @property
    def ingredients(self):
        return copy(self._ingredients)

    @ingredients.setter
    def ingredients(self, ingredients):
        self._ingredients = copy(ingredients)

    @property
    def image(self):
        return deepcopy(self._image)

    @image.setter
    def image(self, image):
        self._image = deepcopy(image)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
