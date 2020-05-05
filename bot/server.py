import argparse
import requests

from flask import request, Flask


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
            self.model = None # TFIdfCocktailModel(self.train).train_on_recipes()
        elif self.model_name == 'BertCocktailModel':
            self.model = None # BertCocktailModel(self.model_config_file, self.model_vocab_file)
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


def parse_server_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default='8888')
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--web-hook-url', type=str, required=True)

    return parser.parse_args()


# TODO: merge with GetDrunkTelegramBot
class GetDrunkHandler:
    """Handles user request"""
    def __init__(self, token, hook_url):
        self.bot_url = f"https://api.telegram.org/bot{token}"
        self._set_web_hook(hook_url)

    def _set_web_hook(self, hook_url):
        method = "setWebhook"
        url = f"{self.bot_url}/{method}"
        data = {"url": hook_url}
        requests.post(url, data=data)

    def __call__(self, chat_id, user_request_data):
        # TODO: add server logic
        self._send_message(chat_id, user_request_data)

    def _send_message(self, chat_id, text):
        method = "sendMessage"
        url = f"{self.bot_url}/{method}"
        data = {"chat_id": chat_id, "text": text}
        requests.post(url, data=data)


def create_server(args):
    app = Flask(__name__)
    handler = GetDrunkHandler(token=args.token, hook_url=args.web_hook_url)

    @app.route('/', methods=['GET', 'POST'])
    def post():
        """
        Handles every user message.
        """

        if request.method == "POST":
            # data format may differ
            data = request.get_json(force=True)
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]

            print("Got a message: <%s>." % text)

            handler(chat_id, text)
        else:
            return "Hello, world!"

        return {"ok": True}

    return app


if __name__ == '__main__':
    args = parse_server_args()
    app = create_server(args)

    # use_reloader is false due to problems with CUDA and multiprocessing
    app.run(port=args.port, debug=False, use_reloader=False)
