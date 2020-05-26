import json

from tests.utils import client, make_message_from_text  # noqa: F401


def test_server_responses(client):  # noqa: F811
    rv = client.post('/', json=make_message_from_text('\\start'))
    response = json.loads(rv.data.decode('utf-8'))
    assert response == {'ok': True}
