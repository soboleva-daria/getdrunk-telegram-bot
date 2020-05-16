import json
from pytest import fixture

from get_drunk_telegram_bot.bot.server import create_server

from utils import TelegramInterfaceMocker


class FakeArgs:
    token = None
    web_hook_url = None
    debug = False


@fixture
def client():
    with TelegramInterfaceMocker():
        test_app = create_server(FakeArgs())
        yield test_app.test_client()


def make_message_from_text(text):
    return {
        'message': {
            'chat': {'id': ""},
            'text': text
        }
    }


def test_server_responses(client):
    rv = client.post('/', json=make_message_from_text('\\start'))
    response = json.loads(rv.data.decode('utf-8'))
    assert response == {"ok": True}
