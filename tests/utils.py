from unittest.mock import patch

from get_drunk_telegram_bot.bot.server import GetDrunkBotHandler


class FakeInterface:
    def __init__(self, *args, **kwargs):
        pass

    def _set_web_hook(self, *args, **kwargs):
        return "oops"

    def _send_photo(self, chat_id, text, photo_path):
        self.saved_text = text
        self.saved_photo_path = photo_path

    def _send_message(self, chat_id, text):
        self.saved_text = text


class TelegramInterfaceMocker:
    def __init__(self):
        self.patcher = patch.object(
            GetDrunkBotHandler,
            '__bases__', (FakeInterface,)
        )  # Dark magic is here :)

    def __enter__(self):
        result = self.patcher.__enter__()
        self.patcher.is_local = True
        return result

    def __exit__(self, *args, **kwargs):
        return self.patcher.__exit__(*args, **kwargs)
