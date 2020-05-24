from get_drunk_telegram_bot.bot.server import ServerDataBase
from tests.utils import get_handler, run_test_request, tmp_dir


def test_db_complex_scenario(tmp_dir):
    """
    test controls that db is being updated, dumped and cleaned correctly
    during the user session.
    """
    handler = get_handler()
    handler.db.json_path = f'{tmp_dir}/db.json'

    # sending 5 requests to save in user's history
    for _ in range(5):
        run_test_request(handler, '\\recipe')

    assert (
        len(handler.db.db['']['cocktails_history']) == 5
    ), """
        Cocktails history didn't update properly.
    """

    # check loading from json
    test_db = ServerDataBase(handler.db.json_path)
    assert (
        len(test_db.db['']['cocktails_history']) == 5
    ), """
        dump/load of DB failed.
    """

    run_test_request(handler, '\\end')

    # check db is empty after end of session
    assert (
        len(handler.db.db['']['cocktails_history']) == 0
    ), """
        Cocktails history didn't is not empty after \\end.
    """

    # check saved json is empty after end of session
    test_db = ServerDataBase(handler.db.json_path)
    assert (
        len(test_db.db['']['cocktails_history']) == 0
    ), """
        dump/load of DB failed.
    """
