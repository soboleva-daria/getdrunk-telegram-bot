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


def test_menu():
    handler = get_handler()
    response, _ = run_test_request(handler, "\\menu")
    assert response
    assert type(response) is str
    pass


def test_recipe():
    handler = get_handler()
    _, _ = run_test_request(handler, "\\start")

    correct_response = """
        Pina Colada 🍍 🥃

        Ingredients: 3 cl rum, 3 cl coconut cream, 9 cl pineapple juice

        Method: Mixed with crushed ice in blender until smooth,\
 then pour into a chilled glass, garnish and serve.

        Enjoy! 💫
    """
    correct_response = '\n'.join(
        [line.strip() for line in correct_response.split('\n')]
    )
    response, _ = run_test_request(handler, "\\recipe {}".format(
        ['3 cl rum', '3 cl coconut cream', '9 cl pineapple juice']))
    assert response
    assert type(response) is str
    assert response == correct_response


def test_intoxication_level():
    handler = get_handler()
    _, _ = run_test_request(handler, "\\start")

    correct_response1 = "Sobriety"
    response1, _ = run_test_request(handler, "\\intoxication level")
    assert response1
    assert type(response1) is str
    assert response1.split()[3] == correct_response1

    # 4 glasses of Pina Colada is enough to switch the stage
    for i in range(4):
        _, _ = run_test_request(handler, "\\recipe {}".format(
            ['3 cl rum', '3 cl coconut cream', '9 cl pineapple juice']))
    correct_response2 = "Euphoria"
    response2, _ = run_test_request(handler, "\\intoxication level")
    assert response2
    assert type(response2) is str
    assert response2.split()[3] == correct_response2


def test_info():
    handler = get_handler()
    _, _ = run_test_request(handler, "\\start")

    correct_response1 = "Oh 🤗 looks like you didn't select the cocktail. " \
        "Let's try again, just say \\recipe!"

    response1, _ = run_test_request(handler, "\\info")
    assert response1
    assert type(response1) is str
    assert response1 == correct_response1

    _, _ = run_test_request(handler, "\\recipe {}".format(
        ['3 cl rum', '3 cl coconut cream', '9 cl pineapple juice']))

    correct_response2 = """
         Pina Colada 🍍 🥃 was officially invented on August 15 1954\
 by a bartender named Ramón “Monchito” Marrero! 🔬
    """
    response2, _ = run_test_request(handler, "\\info")
    correct_response2 = '\n'.join(
            [line.strip() for line in correct_response2.split('\n')]
    )
    assert response2
    assert type(response2) is str
    assert response2 == correct_response2


def test_recipe_of_the_day():
    handler = get_handler()
    _, _ = run_test_request(handler, "\\start")

    response1_same_day, _ = run_test_request(handler, "\\recipe of the day")
    response2_same_day, _ = run_test_request(handler, "\\recipe of the day")
    assert response1_same_day
    assert response2_same_day
    assert response1_same_day == response2_same_day


def test_explore():
    # TODO: add //explore functionality
    pass
