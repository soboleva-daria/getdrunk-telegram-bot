import requests
import random
import pickle
import os
import pathlib
import dill
import pandas as pd

from flask import request, Flask
from string import punctuation
from datetime import datetime
from copy import copy, deepcopy

from get_drunk_telegram_bot.model.predict import (
    BaseModel, TFIdfCocktailModel, BertCocktailModel)

from get_drunk_telegram_bot.drinks.cocktail import Cocktail


UTILS_PATH = pathlib.Path('get_drunk_telegram_bot/utils')


class TelegramInterface:
    def __init__(self, token, hook_url, debug=False):
        if debug:
            print('Starting tg interface...')
        self._bot_url = f"https://api.telegram.org/bot{token}"
        self._set_web_hook(hook_url)
        self._chat_id = None
        if debug:
            print('tg interface started successfully.')

    def _set_web_hook(self, hook_url):
        method = "setWebhook"
        url = f"{self._bot_url}/{method}"
        data = {"url": hook_url}
        requests.post(url, data=data)

    def _send_photo(self, chat_id, text, photo_path):
        method = "sendPhoto"
        url = f"{self._bot_url}/{method}"
        data = {"chat_id": chat_id, 'caption': text}
        with open(photo_path, "rb") as image_file:
            requests.post(url, data=data, files={"photo": image_file})

    def _send_message(self, chat_id, text):
        method = "sendMessage"
        url = f"{self._bot_url}/{method}"
        data = {"chat_id": chat_id, "text": text}
        requests.post(url, data=data)


class ServerDataBase:
    def __init__(self, save_path):
        self.json_path = save_path
        if os.path.exists(save_path):
            with open(save_path, 'rb') as f:
                self.db = pickle.load(f)
        else:
            self.db = {}

    def _initialize_record_if_needed(self, chat_id):
        if chat_id not in self.db:
            self.db[chat_id] = {
                'total_alcohol_absorbed': 0,
                'cocktails_history': [],
                'cocktail': None
            }

    def update(self, chat_id, cocktail):
        self._initialize_record_if_needed(chat_id)

        self.db[chat_id]['cocktails_history'].append(cocktail)
        self.db[chat_id]['cocktail'] = cocktail
        self.db[chat_id]['total_alcohol_absorbed'] += \
            cocktail.abv * cocktail.volume

        self._dump()

    def get_cocktail(self, chat_id):
        self._initialize_record_if_needed(chat_id)
        return self.db[chat_id]['cocktail']

    def get_cocktails_history(self, chat_id):
        self._initialize_record_if_needed(chat_id)
        return self.db[chat_id]['cocktails_history']

    def get_total_alcohol_absorbed(self, chat_id):
        self._initialize_record_if_needed(chat_id)
        return self.db[chat_id]['total_alcohol_absorbed']

    def end_current_session(self, chat_id):
        if chat_id in self.db:
            self.db[chat_id] = {
                "total_alcohol_absorbed": 0,
                "cocktails_history": [],
                "cocktail": None,
            }
            self._dump()

    def _dump(self):
        with open(self.json_path, 'wb') as f:
            pickle.dump(self.db, f)


class GetDrunkBotHandler(TelegramInterface):
    # TODO: add exploratory user request
    # TODO: Better formatting for special names? cocktail name etc.
    # TODO: more information for user about what cocktail is currently processing.
    # TODO: user should have an opportunity to provide bac in the begnning and maybe weight?
    def __init__(
            self,
            model_name='BaseModel',
            train=None,
            model_config_file=None,
            model_vocab_file=None,
            debug=False,
            **telegram_kwargs
    ):
        super(GetDrunkBotHandler, self).__init__(
            **telegram_kwargs, debug=debug)

        self.model_name = model_name
        self.train = train
        self.model_config_file = model_config_file
        self.model_vocab_file = model_vocab_file
        self.model = None
        self._create_model()

        # TODO: use custom db path here
        self.db = ServerDataBase(save_path='./db.pkl')

        self.recipes_of_the_day = self.load_recipes_of_the_day()
        print(self.recipes_of_the_day)

        # index of the cocktail in recipe of the day list, refactor here
        self.index = None

        self.debug = debug
        self._create_model()

    def _create_model(self):
        if self.model_name == 'BaseModel':
            self.model = BaseModel()
        elif self.model_name == 'TFIdfCocktailModel':
            self.model = TFIdfCocktailModel(self.train).train_on_recipes()
        elif self.model_name == 'BertCocktailModel':
            self.model = BertCocktailModel(self.model_config_file, self.model_vocab_file)
        else:
            raise ValueError(
                f"Error in model_name. Available models: "
                f"{['TFIdfCocktailModel', 'BertCocktailModel', 'BaseModel']}, "
                f"Got: {self.model_name}")

    def process_message(self, chat_id, msg):
        if self.debug:
            print("Got a message: <%s>." % msg)

        if msg == '\\start'.strip():
            self._start_session_and_say_hello(chat_id)

        elif msg == '\\end':
            self._end_session_and_say_bye(chat_id)

        elif msg == '\\recipe of the day':
            self._send_day_cocktail(chat_id)

        elif '\\recipe' in msg:
            ingredients = self.parse_ingredients(msg)
            self._send_best_cocktail_with_ingredients(chat_id, ingredients)

        elif msg == '\\photo':
            self._send_cocktail_image(chat_id, self.db.get_cocktail(chat_id))

        elif msg == '\\intoxication level':
            self._send_intoxication_degree(chat_id)

        elif msg == '\\info':
            self._send_cocktail_useful_info(chat_id,
                                            self.db.get_cocktail(chat_id))

        elif msg == '\\menu':
            self._send_cocktails_menu(chat_id)

        elif '\\explore' in msg:
            ingredients = self.parse_ingredients(msg)
            self._send_exploration_result(chat_id, ingredients)
        else:
            self._send_help_message(chat_id)

    def _start_session_and_say_hello(self, chat_id):
        self.db.end_current_session(chat_id)
        msg = self.normalize_text("""
            Hey there, wanna get drunk? 💫
            
            Here is what I can do for you:
            
            — find cocktail recipe with your ingredients 🥂
            
            — tell your current intoxication level 🐙
            
            — provide recipe of the day 💜
            
            — explore cocktails for you  💻
        """)

        self._send_message(chat_id, msg)

    def _end_session_and_say_bye(self, chat_id):
        msg = self.normalize_text("""
            Your cocktail history is empty now.
            You’re welcome anytime! ❤️
            Bye 🥂
        """)
        self.db.end_current_session(chat_id)
        self._send_message(chat_id, msg)

    def _send_best_cocktail_with_ingredients(self, chat_id, ingredients):
        if self.debug:
            print('Model predict starts.')
        cocktail = self.model.predict(ingredients)

        msg = self.normalize_text(f"""
            { cocktail.name }
            
            Ingredients: { ', '.join(cocktail.ingredients).strip() }
            
            Method: { cocktail.recipe }  
            
            Enjoy! 💫
        """)

        self.db.update(chat_id, cocktail)

        self._send_message(chat_id, msg)

    def _send_cocktail_image(self, chat_id, cocktail):
        if cocktail is None:
            msg = "Oh 🤗 looks like you didn't select the cocktail. " \
                  "Let's try again, just say \\recipe!"
            self._send_message(chat_id, msg)
        else:
            # TODO: fix here to send real image
            msg = self.normalize_text(f"""
                { cocktail.name }
            """)
            self._send_photo(chat_id, msg, photo_path=str(
                UTILS_PATH.joinpath(f'{cocktail.orig_name}.png')))

    def _send_intoxication_degree(self, chat_id):
        cocktail_list = '\n'.join([
            cocktail.name
            for cocktail in self.db.get_cocktails_history(chat_id)
        ])
        degree = self._get_intoxication_degree(chat_id)
        msg = self.normalize_text(f"""
            You are in {degree}.
            
            Here is the list of what you took: 
            {cocktail_list}
        """)
        self._send_message(chat_id, msg)

    def _get_intoxication_degree(self, chat_id):
        # 170 is avg female weight in the US in pounds, TODO: fix here
        total_alcohol_absorbed = self.db.get_total_alcohol_absorbed(chat_id)
        bac = 100 * total_alcohol_absorbed / 77110.7 / 0.55
        if self.debug:
            print('BAC', bac, total_alcohol_absorbed)
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

    def _send_cocktail_useful_info(self, chat_id, cocktail):
        if cocktail is None:
            msg = "Oh 🤗 looks like you didn't select the cocktail. " \
                  "Let's try again, just say \\recipe!"
        else:
            msg = self.normalize_text(f"""
                {cocktail.name} {cocktail.useful_info}! 🔬
            """)
        self._send_message(chat_id, msg)

    def _send_day_cocktail(self, chat_id):
        weekday_name = datetime.today().strftime("%A")

        if self.index is None:
            self.index = random.randint(0, len(self.recipes_of_the_day))
        cocktail = self.recipes_of_the_day[self.index]
        msg = self.normalize_text(f"""
            Our {weekday_name} menu 👩‍🍳🥳:
            
            {cocktail.name}
            
            Ingredients: {', '.join(cocktail.ingredients).strip()}
            
            Method: {cocktail.recipe}  
                    
            Enjoy! 💫
        """)
        print('KEK', type(cocktail))

        self.db.update(chat_id, cocktail)
        self._send_message(chat_id, msg)

    def _send_cocktails_menu(self, chat_id):
        cocktail_list = '\n'.join([
            cocktail.name for cocktail in self.recipes_of_the_day])
        msg = self.normalize_text(f"""
            Menu 🍽️ 😋:
            
            {cocktail_list.strip()}
        """)
        self._send_message(chat_id, msg)

    def _send_help_message(self, chat_id):
        msg = self.normalize_text("""
            I am sorry :( I did not get what you mean.
            
            Please try again with these commands: 
            `\\start`, `\\end`, `\\recipe`, `\\photo`,
            `\\intoxication level`, `\\recipe of the day`,
            `\\explore`, `\\info`, `\\menu`
            
            Thank you! 🙏
        """)

        self._send_message(chat_id, msg)

    def _send_exploration_result(self, chat_id, ingredients):
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
    def normalize_text(text):
        return '\n'.join([line.strip() for line in text.split('\n')])
    
    @staticmethod
    def parse_ingredients(msg):
        # TODO: might be done in different format
        try:
            return msg[msg.index('\\recipe') + len('\\recipe'):].strip().split(punctuation)
        except ValueError:
            return []

    # TODO: put this method into drinks/preprocessing later?
    @staticmethod
    def load_recipes_of_the_day():
        data = pd.read_csv(str(UTILS_PATH.joinpath('05-CocktailRecipes.csv')))[
            ['RecipeName', 'Ingredients', 'Preparation', 'IMAGE', 'ABV',
             'VOLUME', 'AUTHOR', 'LOCATION', 'OriginalRecipeSource']
        ]
        with open(str(UTILS_PATH.joinpath('emoji.pkl')), 'rb') as fin:
            emojis = pickle.load(fin)

        recipes = []
        for row in data.iterrows():
            # TODO restructure?
            (
                name, ingredients, recipe, image, abv,
                volume, author, location, source
            ) = row[1]

            orig_name = name.replace('_', '').strip()
            name_with_emoji = emojis[name.replace('_', '').strip()]
            ingredients = map(lambda x: x.strip(), ingredients.split('\n'))
            recipe = recipe.strip()
            author = str(author).strip()
            location = str(location).strip()

            useful_info = (
                f"was officially invented by the bartender "
                f"named {author} in {location}"
                if author != 'nan'
                else f"was officially found in the source: {source}"
            )

            abv = float(abv)
            volume = float(volume)
            recipes.append(Cocktail(orig_name, name_with_emoji, ingredients, recipe, image, useful_info, abv, volume))

        return recipes


def create_server(args):
    app = Flask(__name__)
    if args.debug:
        print('Init Bot')
    get_drunk_bot = GetDrunkBotHandler(
        token=args.token, hook_url=args.web_hook_url, debug=args.debug
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
