import difflib
import json
import logging
import os
import pickle
import random
from datetime import datetime
from io import BytesIO
from string import punctuation
from typing import List

import numpy as np
import pandas as pd
import requests
from flask import Flask, request
from lazy import lazy
from pkg_resources import Requirement, resource_filename

from get_drunk_telegram_bot.drinks.cocktail import Cocktail
from get_drunk_telegram_bot.drinks.dataset import Dataset
from get_drunk_telegram_bot.embeder import BertEmbeder, TfidfEmbeder
from get_drunk_telegram_bot.model import BaseModel, EmbederModel
from get_drunk_telegram_bot.similarity import CosineSimilarity
from get_drunk_telegram_bot.utils.utils import decode_json, encode_json, normalize_text

_EMBEDER_MAX_SIMILARITY = 0.79
_EMBEDER_MIN_SIMILARITY = 0.3
_EXPLORE_COCKTAILS_NUM = 3

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def get_file(filename):
    return resource_filename(
        Requirement.parse('get_drunk_telegram_bot'),
        f'get_drunk_telegram_bot/utils/{filename}',
    )


class TelegramInterface:
    """
    TelegramInterface class provides the basic functionality for
    GetDrunkBotHandler.

    :param token: str, telegram bot token

    :param hook_url, telegram bot hook_url (provided by ngrok, see README.md)

    :param debug: bool, specifies the verbosity level (if True, logs will be
    provided in sys.stdout).
    """

    def __init__(self, token, hook_url, debug=False):
        if debug:
            print('Starting tg interface...')
        self._bot_url = f'https://api.telegram.org/bot{token}'
        self._set_web_hook(hook_url)
        self._chat_id = None
        if debug:
            print('tg interface started successfully.')

    def _set_web_hook(self, hook_url):
        method = 'setWebhook'
        url = f'{self._bot_url}/{method}'
        data = {'url': hook_url}
        requests.post(url, data=data)

    def _send_photo(self, chat_id, text, image):
        method = 'sendPhoto'
        url = f'{self._bot_url}/{method}'
        data = {'chat_id': chat_id, 'caption': text}
        byte_io = BytesIO()
        image.save(byte_io, 'png')
        byte_io.seek(0)
        requests.post(url, data=data, files={'photo': byte_io})

    def _send_message(self, chat_id, text):
        method = 'sendMessage'
        url = f'{self._bot_url}/{method}'
        data = {'chat_id': chat_id, 'text': text}
        requests.post(url, data=data)


class ServerDataBase:
    """
    ServerDataBase saves an information about user history of drinks or amount
    of total alcohol absorbed.

    :param save_path: str, path to the local database.
    """

    def __init__(self, save_path):
        self.json_path = save_path
        if os.path.exists(save_path):
            with open(save_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f, object_hook=decode_json)
        else:
            self.db = {}

    def _initialize_record_if_needed(self, chat_id):
        """
        Initializes total_alcohol_absorbed and cocktails history in the
        beginning of the session.

        :param chat_id: str, from which the message was received and where to
        send the response.
        """
        if chat_id not in self.db:
            self.db[chat_id] = {
                'total_alcohol_absorbed': 0,
                'cocktails_history': [],
                'cocktail': None,
            }

    def update(self, chat_id, cocktail):
        """
        Updates cocktails history and total_alcohol_absorbed after
        communication with the user.

        :param chat_id: str, from which the message was received and where to
        send the response;

        :param cocktail: Cocktail instance.
        """
        self._initialize_record_if_needed(chat_id)

        self.db[chat_id]['cocktails_history'].append(cocktail)
        self.db[chat_id]['cocktail'] = cocktail
        self.db[chat_id]['total_alcohol_absorbed'] += cocktail.abv * cocktail.volume

        self._dump()

    def get_cocktail(self, chat_id):
        """
        Returns the most recent cocktail taken by user according to
        communication history.

        :param chat_id: str, from which the message was received and where
        to send the response;

        :return: Cocktail instance, the most recent cocktail taken by user.
        """
        self._initialize_record_if_needed(chat_id)
        return self.db[chat_id]['cocktail']

    def get_cocktails_history(self, chat_id):
        """
        Return full cocktails history for the specific user.

        :param chat_id: str, from which the message was received and where to
        send the response;

        :return: list, full user cocktails history.
        """
        self._initialize_record_if_needed(chat_id)
        return self.db[chat_id]['cocktails_history']

    def get_total_alcohol_absorbed(self, chat_id):
        """
        Return total amount of alcohol absorbed by user.

        :param chat_id: str, from which the message was received and where to
        send the response;

        :return: int, total amount of alcohol absorbed by user.
        """
        self._initialize_record_if_needed(chat_id)
        return self.db[chat_id]['total_alcohol_absorbed']

    def end_current_session(self, chat_id):
        """
        Ends the session with user. Update total_alcohol_absorbed to 0 and
        clean cocktails_history.

        :param chat_id: str, from which the message was received and where to
        send the response;
        """
        if chat_id in self.db:
            self.db[chat_id] = {
                'total_alcohol_absorbed': 0,
                'cocktails_history': [],
                'cocktail': None,
            }
            self._dump()

    def _dump(self):
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, default=encode_json, indent=4)


class GetDrunkBotHandler(TelegramInterface):
    """
    class GetDrunkBotHandler is responsible for all kind of user-server
    communication from processing messages to sending commands in return.

    :param model_name: str, should be one of the {TFIdfCocktailModel,
        BertCocktailModel, BaseModel} (default=BaseModel);

    :param train: str, path to the train table (default=None);

    :param model_config_file: str, path to model config (default=None);

    :param model_vocab_file: str, path to model vocab file (default=None);

    :param debug: bool, specifies the verbosity level (if True, logs will be
        provided in sys.stdout).
    """

    # TODO: add exploratory user request
    # TODO: Better formatting for special names? cocktail name etc.
    # TODO: more information for user about what cocktail is currently processing.  # noqa
    # TODO: user should have an opportunity to provide bac in the begnning and maybe weight?  # noqa
    def __init__(
        self,
        model_name='TFIdfCocktailModel',
        train=None,
        model_config_file=None,
        model_vocab_file=None,
        debug=False,
        **telegram_kwargs,
    ):
        super(GetDrunkBotHandler, self).__init__(**telegram_kwargs, debug=debug)

        self.model_name = model_name
        self.train = train
        self.model_config_file = model_config_file
        self.model_vocab_file = model_vocab_file
        self.model = None
        self.dataset = Dataset()
        self._create_model()

        # TODO: use custom db path here
        self.db = ServerDataBase(save_path='./db.json')

        # index of the cocktail in recipe of the day list, refactor here
        self.index = None

        self.debug = debug
        self._create_model()

    def _create_model(self):
        similarity = CosineSimilarity()
        if self.model_name == 'BaseModel':
            self.model = BaseModel()
        elif self.model_name == 'TFIdfCocktailModel':
            embeder = TfidfEmbeder()
            self.model = EmbederModel(
                embeder=embeder,
                dataset=self.dataset,
                similarity=similarity,
                max_similarity=_EMBEDER_MAX_SIMILARITY,
                min_similarity=_EMBEDER_MIN_SIMILARITY,
            )
        elif self.model_name == 'BertCocktailModel':
            embeder = BertEmbeder()
            self.model = EmbederModel(
                embeder=embeder,
                dataset=self.dataset,
                similarity=similarity,
                max_similarity=_EMBEDER_MAX_SIMILARITY,
                min_similarity=_EMBEDER_MIN_SIMILARITY,
            )
        else:
            raise ValueError(
                f'Error in model_name. Available models: '
                f"{['TFIdfCocktailModel', 'BertCocktailModel', 'BaseModel']}, "
                f'Got: {self.model_name}'
            )

    def process_message(self, chat_id, msg):
        """
        Process message from user and send the response back.

        :param chat_id: str, from which the message was received and where to
            send the response.
        :param msg: str, message that was sent by user.
        """
        if self.debug:
            print('Got a message: <%s>.' % msg)

        if msg == '\\start'.strip():
            logging.info(f'Start chat with id={chat_id}')
            self._start_session_and_say_hello(chat_id)

        elif msg == '\\end':
            logging.info(f'End chat with id={chat_id}')
            self._end_session_and_say_bye(chat_id)

        elif msg == '\\recipe of the day':
            logging.info(f'Give recipe of the day for chat with id={chat_id}')
            self._send_day_cocktail(chat_id)

        elif '\\recipe' in msg:
            logging.info(f'Give recipe for chat with id={chat_id}')
            ingredients = self.parse_ingredients(msg)
            self._send_best_cocktail_with_ingredients(chat_id, ingredients)

        elif msg == '\\photo':
            logging.info(f'Give photo for chat with id={chat_id}')
            self._send_cocktail_image(chat_id, self.db.get_cocktail(chat_id))

        elif msg == '\\intoxication level':
            logging.info(f'Give intoxication level for chat with id={chat_id}')
            self._send_intoxication_degree(chat_id)

        elif msg == '\\info':
            logging.info(f'Give info for chat with id={chat_id}')
            self._send_cocktail_useful_info(chat_id, self.db.get_cocktail(chat_id))

        elif msg == '\\menu':
            logging.info(f'Give menu for chat with id={chat_id}')
            self._send_cocktails_menu(chat_id)

        elif '\\explore' in msg:
            logging.info(f'Explore for chat with id={chat_id}')
            self._send_exploration_result(chat_id, msg)
        else:
            logging.info(f'Help to chat with id={chat_id}')
            self._send_help_message(chat_id)

    def _start_session_and_say_hello(self, chat_id):
        self.db.end_current_session(chat_id)
        msg = normalize_text(
            """
            Hey there, wanna get drunk? 💫

            Here is what I can do for you:

            — find cocktail recipe with your ingredients 🥂

            — tell your current intoxication level 🐙

            — provide recipe of the day 💜

            — explore cocktails for you  💻
        """
        )

        self._send_message(chat_id, msg)

    def _end_session_and_say_bye(self, chat_id):
        msg = normalize_text(
            """
            Your cocktail history is empty now.
            You’re welcome anytime! ❤️
            Bye 🥂
        """
        )
        self.db.end_current_session(chat_id)
        self._send_message(chat_id, msg)

    def _send_best_cocktail_with_ingredients(self, chat_id, ingredients):
        if self.debug:
            print('Model predict starts.')
        best_cocktails = self.model.predict(' '.join(ingredients))
        if len(best_cocktails) == 0:
            msg = (
                "Oops 😭 We couldn't find cocktail for you\n"
                "Let's try again, just say \\recipe!"
            )
        else:
            cocktail = random.choice(best_cocktails)

            msg = normalize_text(
                f"""
                { cocktail.name }

                Ingredients: { ', '.join(cocktail.pretty_ingredients).strip() }

                Method: { cocktail.recipe }

                Enjoy! 💫
            """
            )

            self.db.update(chat_id, cocktail)

        self._send_message(chat_id, msg)

    def _send_cocktail_image(self, chat_id, cocktail):
        if cocktail is None:
            msg = (
                "Oh 🤗 looks like you didn't select the cocktail. "
                "Let's try again, just say \\recipe!"
            )
            self._send_message(chat_id, msg)
        elif cocktail.image is None:
            msg = (
                "Oh 😭 looks like we don't have image for that cocktail. "
                "Let's try again, just say \\recipe!"
            )
            self._send_message(chat_id, msg)
        else:
            # TODO: fix here to send real image
            msg = normalize_text(
                f"""
                { cocktail.name }
            """
            )
            self._send_photo(chat_id, msg, cocktail.image)

    def _send_intoxication_degree(self, chat_id):
        cocktail_list = '\n'.join(
            [cocktail.name for cocktail in self.db.get_cocktails_history(chat_id)]
        )
        degree = self._get_intoxication_degree(chat_id)
        msg = normalize_text(
            f"""
            You are in {degree}.

            Here is the list of what you took:
            {cocktail_list}
        """
        )
        self._send_message(chat_id, msg)

    def _get_intoxication_degree(self, chat_id):
        # 170 is avg female weight in the US in pounds, TODO: fix here
        total_alcohol_absorbed = self.db.get_total_alcohol_absorbed(chat_id)
        bac = 100 * total_alcohol_absorbed / 77110.7 / 0.55
        if self.debug:
            print('BAC', bac, total_alcohol_absorbed)
        if 0.0 <= bac <= 0.03:
            return 'Sobriety 🙅 stage (1 out of 7)'
        elif 0.03 < bac <= 0.09:
            return 'Euphoria 🦄 stage (2 out of 7)'
        elif 0.09 < bac <= 0.18:
            return 'Excitement 🥳 stage (3 out of 7)'
        elif 0.18 < bac <= 0.30:
            return 'Confusion 🙈 stage (4 out of 7)'
        elif 0.30 < bac <= 0.35:
            return 'Stupor 🐨 stage (5 out of 7)'
        elif 0.35 < bac <= 0.45:
            return 'Coma 🗿 stage (6 out of 7)'
        else:
            return 'Death 💀 stage (7 out of 7). I will miss you 🥺'

    def _send_cocktail_useful_info(self, chat_id, cocktail):
        if cocktail is None:
            msg = (
                "Oh 🤗 looks like you didn't select the cocktail. "
                "Let's try again, just say \\recipe!"
            )
        elif cocktail.useful_info is None:
            msg = (
                "Oh 🤗 looks like we don't have information about this cocktail. "
                "Let's try again, just say \\recipe!"
            )
        else:
            msg = normalize_text(
                f"""
                {cocktail.name} {cocktail.useful_info}! 🔬
            """
            )
        self._send_message(chat_id, msg)

    def _send_day_cocktail(self, chat_id):
        weekday_name = datetime.today().strftime('%A')

        if self.index is None:
            self.index = random.randint(0, len(self.recipes_of_the_day) - 1)
        cocktail = self.recipes_of_the_day[self.index]
        msg = normalize_text(
            f"""
            Our {weekday_name} menu 👩‍🍳🥳:

            {cocktail.name}

            Ingredients: {', '.join(cocktail.pretty_ingredients).strip()}

            Method: {cocktail.recipe}

            Enjoy! 💫
        """
        )

        self.db.update(chat_id, cocktail)
        self._send_message(chat_id, msg)

    def _send_cocktails_menu(self, chat_id):
        cocktail_list = '\n'.join(
            [cocktail.name for cocktail in self.recipes_of_the_day]
        )
        msg = normalize_text(
            f"""
            Menu 🍽️ 😋:

            {cocktail_list.strip()}
        """
        )
        self._send_message(chat_id, msg)

    def _send_help_message(self, chat_id):
        msg = normalize_text(
            """
            I am sorry :( I did not get what you mean.

            Please try again with these commands:
            `\\start`, `\\end`, `\\recipe`, `\\photo`,
            `\\intoxication level`, `\\recipe of the day`,
            `\\explore`, `\\info`, `\\menu`

            Thank you! 🙏
        """
        )

        self._send_message(chat_id, msg)

    def _send_exploration_result(self, chat_id, text):
        start_position = text.index('\\explore') + len('\\explore')

        query = text[start_position:].strip().lower().split()
        query = ' '.join(query)

        right_ingredients = None
        right_cocktail_name = None

        max_ratio = 0.8
        for cocktail_name, ingredients in self.dataset.get_names_and_ingredients():
            ratio = difflib.SequenceMatcher(a=query, b=cocktail_name.lower()).ratio()
            if ratio > max_ratio:
                right_ingredients = ingredients
                right_cocktail_name = cocktail_name
                max_ratio = ratio

        if right_ingredients:
            predictions = self.model.predict(right_ingredients, True)
            cocktails = np.random.choice(
                predictions[1:],
                min(_EXPLORE_COCKTAILS_NUM, len(predictions[1:])),
                replace=False,
            )

            cocktails_msg = '\n'.join(
                [
                    f"""{cocktail.name}

                        Ingredients: {', '.join(cocktail.pretty_ingredients).strip()}

                        Method: {cocktail.recipe}
                        """
                    for cocktail in cocktails
                ]
            )

            msg = normalize_text(
                f""" Some cocktails similar to {right_cocktail_name}:"""
                + '\n\n'
                + cocktails_msg
                + '\n'
                + 'Enjoy! 💫'
            )

        else:
            predictions = self.model.predict(query)
            if len(predictions) > 0:
                cocktails = np.random.choice(
                    predictions,
                    min(_EXPLORE_COCKTAILS_NUM, len(predictions)),
                    replace=False,
                )
                cocktails_msg = '\n'.join(
                    [
                        f"""{cocktail.name}

                        Ingredients: {', '.join(cocktail.pretty_ingredients).strip()}

                        Method: {cocktail.recipe}
                        """
                        for cocktail in cocktails
                    ]
                )

                msg = normalize_text(
                    'Some cocktails with these ingredients:\n\n'
                    + cocktails_msg
                    + '\n'
                    + 'Enjoy! 💫'
                )
            else:
                msg = (
                    "Sorry, I don't know similar cocktails 🥺\n"
                    "Please try to type something like '\\explore rum, lemon' or '\\explore Pina Colada' "
                    'and I will find similary cocktails for you ❤️'
                )
                msg = normalize_text(msg)

        self._send_message(chat_id, msg)

    @staticmethod
    def parse_ingredients(text):
        """
        Provides basic parsing of the ingredients sent by user.

        :param text: str, text from user with ingredients.
        """
        # TODO: might be done in different format
        try:
            start_position = text.index('\\recipe') + len('\\recipe')
            return text[start_position:].strip().split(punctuation)
        except ValueError:
            return []

    @lazy
    def recipes_of_the_day(self, recipes_num: int = 5) -> List[Cocktail]:
        indexes = np.arange(len(self.dataset))
        np.random.shuffle(indexes)
        return self.dataset.get_coctails_by_ids(indexes[:5])

    # TODO: put this method into drinks/preprocessing later?
    @staticmethod
    def nooooo_load_recipes_of_the_day():
        """
        Load information about recipes of the day
        (local 05-CocktailRecipes.csv table).
        """
        data = pd.read_csv(get_file('05-CocktailRecipes.csv'))[
            [
                'RecipeName',
                'Ingredients',
                'Preparation',
                'IMAGE',
                'ABV',
                'VOLUME',
                'AUTHOR',
                'LOCATION',
                'OriginalRecipeSource',
            ]
        ]
        with open(get_file('emoji.pkl'), 'rb') as fin:
            emojis = pickle.load(fin)

        recipes = []
        for row in data.iterrows():
            # TODO restructure?
            (
                name,
                ingredients,
                recipe,
                image,
                abv,
                volume,
                author,
                location,
                source,
            ) = row[1]

            orig_name = name.replace('_', '').strip()
            name_with_emoji = emojis[name.replace('_', '').strip()]
            ingredients = list(map(lambda x: x.strip(), ingredients.split('\n')))
            recipe = recipe.strip()
            author = str(author).strip()
            location = str(location).strip()

            useful_info = (
                f'was officially invented by the bartender '
                f'named {author} in {location}'
                if author != 'nan'
                else f'was officially found in the source: {source}'
            )

            abv = float(abv)
            volume = float(volume)
            recipes.append(
                Cocktail(
                    orig_name,
                    name_with_emoji,
                    ingredients,
                    recipe,
                    image,
                    useful_info,
                    abv,
                    volume,
                )
            )

        return recipes


def create_server(args):
    """
    Starts get-drunk-telegram bot.

    :param args: --port, --token, --web-hook-url and --debug params specified.
    """
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
        if request.method == 'POST':
            # data format may differ
            data = request.get_json(force=True)

            logging.info(f'Got request:\n{data}\n')

            if 'message' in data:
                chat_id = data['message']['chat']['id']
                text = data['message']['text']
            else:
                chat_id = data['edited_message']['chat']['id']
                text = data['edited_message']['text']

            get_drunk_bot.process_message(chat_id, text)
        else:
            return 'Hello, world!'

        return json.dumps({'ok': True})

    return app
