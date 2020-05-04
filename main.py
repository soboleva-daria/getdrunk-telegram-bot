from telethon import TelegramClient
import sys

from .bot.bot import GetDrunkTelegramBot


def main(api_id, api_hash, proxy, connection, model_name, train):
    with TelegramClient('anon', api_id, api_hash, proxy=proxy, connection=connection) as client:

        get_drunk_bot = GetDrunkTelegramBot(client, model_name, train)

        get_drunk_bot.start_session_and_say_hello()

        if get_drunk_bot.ask_for_cocktail_ingredients():
            ingredients = get_drunk_bot.receive_cocktail_ingredients()
            cocktail = get_drunk_bot.choose_best_cocktail_with_ingredients(ingredients)

            if get_drunk_bot.ask_to_send_cocktail_recipe():
                get_drunk_bot.send_cocktail_recipe(cocktail)

            if get_drunk_bot.ask_to_send_cocktail_image():
                get_drunk_bot.send_cocktail_image(cocktail)

            if get_drunk_bot.ask_to_send_cocktail_useful_info():
                get_drunk_bot.send_cocktail_useful_info(cocktail)

            if get_drunk_bot.ask_to_send_intoxication_degree():
                get_drunk_bot.send_intoxication_degree()

            if get_drunk_bot.ask_to_end_session_and_say_bye():
                get_drunk_bot.end_session_and_say_bye()
                # TODO: replace with better end maybe?
                sys.exit(0)


if __name__ == "__main__":
    params = {
        'api_id': "", 'api_hash': "", 'proxy': "", 'connection': "",
        "model_name": "TFIdfCocktailModel", 'train': "./train.tsv"
    }
    main(*params)