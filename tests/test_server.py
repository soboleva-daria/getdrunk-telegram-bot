import json

from tests.utils import client, make_message_from_text


def test_server_responses(client):
    rv = client.post('/', json=make_message_from_text('\\start'))
    response = json.loads(rv.data.decode('utf-8'))
    assert response == {'ok': True}
