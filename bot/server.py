import argparse
import requests

from flask import request, Flask
from string import punctuation

# TODO: fixme later
import sys
sys.path.append('../')

from model.predict import BaseModel, TFIdfCocktailModel, BertCocktailModel
import pandas as pd

from drinks.cocktail import Cocktail
import random
import pickle
from datetime import datetime


class GetDrunkTelegramBot:
    # TODO: add exploratory user request
    # TODO: Better formatting for special names? cocktail name etc.
    # TODO: more information for user about what cocktail is currently processing.
    # TODO: user should have an opportunity to provide bac in the begnning and maybe weight?
    def __init__(
            self,
            token,
            hook_url,
            model_name='BaseModel',
            train=None,
            model_config_file=None,
            model_vocab_file=None,
            debug=False
    ):
        self._bot_url = f"https://api.telegram.org/bot{token}"
        self._set_web_hook(hook_url)
        self._chat_id = None

        self.model_name = model_name
        self.train = train
        self.model_config_file = model_config_file
        self.model_vocab_file = model_vocab_file
        self.model = None
        self.init_model()

        self.cocktail = None
        self.total_alcohol_absorbed = 0
        self.cocktails_history = []
        self.recipes_of_the_day = self.load_recipes_of_the_day()
        self.index = None # index of the cocktail in recipe of the day list, refactor here

        self.debug = debug
        self.init_model()

    def _set_web_hook(self, hook_url):
        method = "setWebhook"
        url = f"{self._bot_url}/{method}"
        data = {"url": hook_url}
        requests.post(url, data=data)

    def _send_message(self, text):
        method = "sendMessage"
        url = f"{self._bot_url}/{method}"
        data = {"chat_id": self._chat_id, "text": text}
        requests.post(url, data=data)

    def init_model(self):
        if self.model_name == 'BaseModel':
            self.model = BaseModel()
        elif self.model_name == 'TFIdfCocktailModel':
            self.model = TFIdfCocktailModel(self.train).train_on_recipes()
        elif self.model_name == 'BertCocktailModel':
            self.model = BertCocktailModel(self.model_config_file, self.model_vocab_file)
        else:
            raise ValueError(
                "Error in model_name. Available models: {}, Got: {}".format(
                    ['TFIdfCocktailModel', 'BertCocktailModel', 'BaseModel'],
                    self.model_name))

    def process_message(self, chat_id, msg):
        self._chat_id = chat_id

        if self.debug:
            print("Got a message: <%s>." % msg)

        if msg == '\start'.strip():
            self._start_session_and_say_hello()

        elif msg == '\end':
            self._end_session_and_say_bye()

        elif msg == '\\recipe of the day':
            self._send_day_cocktail()

        elif '\\recipe' in msg:
            ingredients = self.parse_ingredients(msg)
            self._send_best_cocktail_with_ingredients(ingredients)

        elif msg == '\photo':
            self._send_cocktail_image(self.cocktail)

        elif msg == '\intoxication level':
            self._send_intoxication_degree()

        elif msg == '\info':
            self._send_cocktail_useful_info(self.cocktail)

        elif msg == '\menu':
            self._send_cocktails_menu()

        elif '\explore' in msg:
            ingredients = self.parse_ingredients(msg)
            self._send_exploration_result(ingredients)
        else:
            self._send_help_message()

    def _start_session_and_say_hello(self):
        self.total_alcohol_absorbed = 0
        msg = \
            """
Hey there, wanna get drunk? 💫

Here is what I can do for you:

— find cocktail recipe with your ingredients 🥂

— tell your current intoxication level 🐙

— provide recipe of the day 💜

— explore cocktails for you  💻
            """
        self._send_message(msg)

    def _end_session_and_say_bye(self):
        msg = \
            """
You’re welcome anytime! ❤️
Bye 🥂
            """
        self._send_message(msg)

    def _send_best_cocktail_with_ingredients(self, ingredients):
        self.cocktail = self.model.predict(ingredients)
        msg = \
            """
{}

Ingredients: {}

Method: {}  


Enjoy! 💫
        """.format(self.cocktail.name, ', '.join(self.cocktail.ingredients).strip(), self.cocktail.recipe)
        self.total_alcohol_absorbed += self.cocktail.abv * self.cocktail.volume
        self.cocktails_history.append(self.cocktail)
        self._send_message(msg)

    def _send_cocktail_image(self, cocktail):
        if cocktail is None:
            msg = "Oh 🤗 looks like you didn't select the cocktail. " \
                  "Let's try again, just say \\recipe!"
        else:
            # TODO: fix here to send real image
            msg = \
                """
                {} {}! 🔬
                """.format(cocktail.name, cocktail.image)
        self._send_message(msg)

    def _send_intoxication_degree(self):
        degree = self._get_intoxication_degree()
        msg = \
"""
You are in {}. 

Here is the list of what you took: 
{} 
""".format(degree, '\n'.join([cocktail.name for cocktail in self.cocktails_history]))
        self._send_message(msg)

    def _get_intoxication_degree(self):
        # 170 is avg female weight in the US in pounds, TODO: fix here
        bac = 100 * self.total_alcohol_absorbed / 77110.7 / 0.55
        print('BAC', bac)
        if self.debug:
            print('BAC', bac, self.total_alcohol_absorbed)
        if 0.0 <= bac <= 0.03:
            return "Sobriety 🙅 stage (1 out of 7)"
        elif 0.03 < bac <= 0.09:
            return 'Euphoria 🦄 stage (2 out of 7)'
        elif 0.09 < bac <= 0.18:
            return 'Excitement 🥳 stage (3 out of 7)'
        elif 0.18 < bac <= 0.30:
            return 'Confusion 🙈 stage (4 out of 7)'
        elif 0.30 < bac <= 0.35:
            return "Stupor 🐨 stage (5 out of 7)"
        elif 0.35 < bac <= 0.45:
            return 'Coma 🗿 stage (6 out of 7)'
        else:
            return 'Death 💀 stage (7 out of 7). I will miss you 🥺'

    def _send_cocktail_useful_info(self, cocktail):
        if cocktail is None:
            msg = "Oh 🤗 looks like you didn't select the cocktail. " \
                  "Let's try again, just say \\recipe!"
        else:
            msg = \
    """
    {} {}! 🔬
    """.format(cocktail.name, cocktail.useful_info)
        self._send_message(msg)

    def _send_day_cocktail(self):
        weekday_name = datetime.today().strftime("%A")

        if self.index is None:
            self.index = random.randint(0, len(self.recipes_of_the_day))

        self.cocktail = self.recipes_of_the_day[self.index]
        msg = \
            """
Our {} menu 👩‍🍳🥳:

{}

Ingredients: {}

Method: {}  


Enjoy! 💫
        """.format(weekday_name, self.cocktail.name, ', '.join(self.cocktail.ingredients).strip(), self.cocktail.recipe)

        self.total_alcohol_absorbed += self.cocktail.abv * self.cocktail.volume
        self.cocktails_history.append(self.cocktail)
        self._send_message(msg)

    def _send_cocktails_menu(self):
        msg = \
"""
Menu 🍽️ 😋: 

{} 
""".format('\n'.join([cocktail.name for cocktail in self.recipes_of_the_day]))
        self._send_message(msg)

    def _send_help_message(self):
        msg = \
"""
I am sorry :( I did not get what you mean.

Please try again with these commands: 
`\start`, `\end`, `\\recipe`, `\photo`, `\intoxication level`, `\\recipe of the day`, `\explore`, `\info`, `\menu`

Thank you! 🙏
"""

        self._send_message(msg)

    def _send_exploration_result(self):
        pass

    # TODO: do we need these methods?
    # def ask_for_cocktail_ingredients(self):
    #     pass

    # def ask_to_end_session_and_say_bye(self):
    #     pass

    # def ask_to_send_cocktail_recipe(self):
    #     pass

    # def ask_to_send_cocktail_image(self):
    #     pass
    #
    # def ask_to_send_cocktail_useful_info(self):
    #     pass

    # def ask_to_send_day_recipe(self):
    #     pass
    @staticmethod
    def parse_ingredients(msg):
        # TODO: might be done in different format
        return msg[msg.index('\\recipe') + len('\\recipe'):].strip().split(punctuation)

    # TODO: put this method into drinks/preprocessing later?
    @staticmethod
    def load_recipes_of_the_day():
        data = pd.read_csv('../utils/05-CocktailRecipes.csv')[
            ['RecipeName', 'Ingredients', 'Preparation', 'IMAGE', 'INFO', 'ABV', 'VOLUME']
        ]
        with open('../utils/emoji.pkl', 'rb') as fin:
            emojis = pickle.load(fin)

        recipes = []
        for row in data.iterrows():
            # TODO restructure?
            name, ingredients, recipe, image, useful_info, abv, volume = row[1]
            name_with_emoji = emojis[name.replace('_', '').strip()]
            ingredients = map(lambda x: x.strip(), ingredients.split('\n'))
            recipe = recipe.strip()
            useful_info = useful_info.strip()
            abv = float(abv)
            volume = float(volume)
            recipes.append(Cocktail(name_with_emoji, ingredients, recipe, image, useful_info, abv, volume))

        print('RECIPES', recipes[0].name, recipes[-1].name)
        return recipes


def parse_server_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default='8888')
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--web-hook-url', type=str, required=True)
    parser.add_argument('--debug', type=bool, default=False, nargs='?')
    return parser.parse_args()


def create_server(args):
    app = Flask(__name__)

    get_drunk_bot = GetDrunkTelegramBot(
        token=args.token, hook_url=args.web_hook_url
    )

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

            get_drunk_bot.process_message(chat_id, text)
        else:
            return "Hello, world!"

        return {"ok": True}

    return app


if __name__ == '__main__':
    args = parse_server_args()
    app = create_server(args)

    # use_reloader is false due to problems with CUDA and multiprocessing
    app.run(port=args.port, debug=True, use_reloader=False)
