from utils import get_handler, tmp_dir, run_test_request


def test_start():
    handler = get_handler()
    response, _ = run_test_request(handler, "\\start")
    assert response
    assert type(response) is str


def test_end():
    handler = get_handler()
    response, _ = run_test_request(handler, "\\end")
    assert response
    assert type(response) is str
