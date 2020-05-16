from pytest import fixture

from get_drunk_telegram_bot.bot.server import (
    GetDrunkBotHandler, ServerDataBase)

from utils import TelegramInterfaceMocker


@fixture
def tmp_dir(tmpdir):
    return str(tmpdir)


def get_handler():
    with TelegramInterfaceMocker():
        return GetDrunkBotHandler()


def run_test_request(handler, text):
    with TelegramInterfaceMocker():
        handler.process_message("", text)

        text = getattr(handler, 'saved_text', None)
        im_path = getattr(handler, 'saved_photo_path', None)

        # Maybe some assert here (common for all requests)

        return (text, im_path)


def test_start():
    handler = get_handler()
    response, _ = run_test_request(handler, "\\start")
    assert len(response) > 10
    assert GetDrunkBotHandler.normalize_text(response) == response, """
        No indents in response. Use GetDrunkBotHandler.normalize_text(text).
    """


def test_end():
    handler = get_handler()
    response, _ = run_test_request(handler, "\\end")
    assert len(response) > 10
    assert GetDrunkBotHandler.normalize_text(response) == response, """
        No indents in response. Use GetDrunkBotHandler.normalize_text(text).
    """


def test_db_complex_scenario(tmp_dir):
    handler = get_handler()
    handler.db.json_path = f'{tmp_dir}/db.json'
    for _ in range(5):
        run_test_request(handler, '\\recipe')

    assert len(handler.db.db[""]["cocktails_history"]) == 5, """
        Cocktails history didn't update properly.
    """

    test_db = ServerDataBase(handler.db.json_path)
    assert len(test_db.db[""]["cocktails_history"]) == 5, """
        dump/load of DB failed.
    """

    run_test_request(handler, '\\end')

    assert len(handler.db.db[""]["cocktails_history"]) == 0, """
        Cocktails history didn't is not empty after \\end.
    """

    test_db = ServerDataBase(handler.db.json_path)
    assert len(test_db.db[""]["cocktails_history"]) == 0, """
        dump/load of DB failed.
    """
