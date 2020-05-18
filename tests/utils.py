from unittest.mock import patch
from pytest import fixture

from get_drunk_telegram_bot.bot.server import GetDrunkBotHandler, create_server


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


def canonical_normalization(text):
    return '\n'.join([line.strip() for line in text.split('\n')])


@fixture
def tmp_dir(tmpdir):
    return str(tmpdir)


@fixture
def client():
    with TelegramInterfaceMocker():
        test_app = create_server(FakeArgs())
        yield test_app.test_client()


class FakeArgs:
    token = None
    web_hook_url = None
    debug = False


def make_message_from_text(text):
    return {
        'message': {
            'chat': {'id': ""},
            'text': text
        }
    }


def get_handler():
    with TelegramInterfaceMocker():
        return GetDrunkBotHandler()


def run_test_request(handler, text, control_normalization=True):
    with TelegramInterfaceMocker():
        handler.process_message("", text)

        text = getattr(handler, 'saved_text', None)
        im_path = getattr(handler, 'saved_photo_path', None)

        # Maybe some assert here (common for all requests)
        if control_normalization:
            assert canonical_normalization(text) == text, (
                "No indents in response."
                "Use GetDrunkBotHandler.normalize_text(text)."
            )

        return (text, im_path)
