from ..model.predict import TFIdfCocktailModel, BertCocktailModel


class GetDrunkTelegramBot:
    # TODO: add exploratory user request
    # TODO: add specified user request
    # TODO: add recipe of the day request
    def __init__(self, client, model_name='TFIdfCocktailModel', train=None, model_config_file=None, model_vocab_file=None):
        self.client = client
        self.model_name = model_name
        self.train = train
        self.model_config_file = model_config_file
        self.model_vocab_file = model_vocab_file
        self.model = None
        self.init_model()
        pass

    def init_model(self):
        if self.model_name == 'TFIdfCocktailModel':
            self.model = TFIdfCocktailModel(self.train).train_on_recipes()
        elif self.model_name == 'BertCocktailModel':
            self.model = BertCocktailModel(self.model_config_file, self.model_vocab_file)
        else:
            raise ValueError(
                "Error in model_name. Available models: {}, Got: {}".format(
                    ['TFIdfCocktailModel', 'BertCocktailModel'],
                    self.model_name))

    def start_session_and_say_hello(self):
        pass

    def ask_to_end_session_and_say_bye(self):
        pass

    def end_session_and_say_bye(self):
        pass

    def ask_for_cocktail_ingredients(self):
        pass

    def receive_cocktail_ingredients(self):
        pass

    def choose_best_cocktail_with_ingredients(self, ingredients):
        return self.model.predict(ingredients)

    def ask_to_send_cocktail_recipe(self):
        pass

    def send_cocktail_recipe(self, cocktail):
        pass

    def ask_to_send_cocktail_image(self):
        pass

    def send_cocktail_image(self, cocktail):
        pass

    def ask_to_send_cocktail_useful_info(self):
        pass

    def send_cocktail_useful_info(self, cocktail):
        pass

    def ask_to_send_intoxication_degree(self):
        pass

    def send_intoxication_degree(self):
        pass
