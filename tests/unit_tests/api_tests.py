import string
import api
import party
import test_db_manager
import os


# To maintain consistency across tests, PARTIES is cleared
# A party with code "test_party_code" is added with a single gladiator, "test_token"
def default_party_setup():
    party.PARTIES = dict()
    test_party = party.Party()
    test_party.add_gladiator("test_token")
    party.PARTIES["test_party_code"] = test_party


token = "test_token"
query_string = []
test_pipe_reader = -1


# When calling, always call os.close(test_pipe_reader) when finished
def setup_api(tmp_path, monkeypatch):
    global test_pipe_reader
    tmp_dir = str(tmp_path)
    www_dir = os.path.join(tmp_dir, "www")

    os.mkdir(www_dir)
    html_file = os.path.join(www_dir, "index.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("<html><body>Hello</body></html>")

    result_pipe = os.path.join(tmp_dir, "result_pipe")
    test_pipe = os.path.join(tmp_dir, "test_pipe")

    os.mkfifo(result_pipe)
    os.mkfifo(test_pipe)

    # (I don't actually know how the following works but it just does ¯\_(ツ)_/¯)

    # Change working directory so "result_pipe" resolves correctly
    monkeypatch.chdir(tmp_path)

    # Open a reader so that opening "result pipe" doesn't block
    test_pipe_reader = os.open(test_pipe, os.O_RDONLY | os.O_NONBLOCK)

    CODE_CHARS = string.ascii_lowercase + string.digits
    CODE_LENGTH = 5

    api.init(
        path=str(www_dir),
        code_chars=CODE_CHARS,
        code_length=CODE_LENGTH,
    )


# INIT
def test_init(tmp_path, monkeypatch):
    try:
        setup_api(tmp_path, monkeypatch)

        # Ensure HTML was loaded
        assert ("index.html",) in api.SERVABLE
        assert b"Hello" in api.SERVABLE[("index.html",)]

        # Pipes should be valid file descriptors
        assert api.RESULT_PIPE >= 0
        assert api.TEST_PIPE >= 0
    finally:
        os.close(api.RESULT_PIPE)
        os.close(api.TEST_PIPE)
        os.close(test_pipe_reader)


# FIND_PARTY
def test_find_party_valid():
    default_party_setup()
    print(api.find_party(token))

    assert api.find_party(token) == "test_party_code"


def test_find_party_invalid():
    assert api.find_party("invalid_test_token") == ""


# FORMAT_ERROR
def test_format_error_valid():
    assert api.format_error(222, "test body") == (
        222,
        tuple(),
        b"<!DOCTYPE html><body><h1>Error: 222!!</h1><p>test body</p></body>",
    )


# TODO
# POLL RESULT PIPE


# LOBBY
def test_lobby_valid_code():
    api.SERVABLE[("pages", "lobby.html")] = ("pages", "index.html")
    default_party_setup()
    query_string = [("p", "test_party_code")]

    assert api.lobby(token, query_string) == (200, tuple(), ("pages", "index.html"))


def test_lobby_glad_switch():
    party.PARTIES = dict()
    api.CODE_CHARS = "abc"
    api.CODE_LENGTH = 5
    test_party = party.Party()
    party.PARTIES["test_party_code"] = test_party
    test_party.add_gladiator("test_token")

    token = "test_token"
    query_string = []

    assert api.lobby(token, query_string)[0] == 303
    # print(api.lobby(token, query_string))
    for p in party.PARTIES:
        print(party.PARTIES[p].gladiators)
    print("parties at: " + str(party.PARTIES))
    assert api.find_party("test_token") != "test_party_code"
    assert api.find_party("test_token") != ""


def test_lobby_creation():
    party.PARTIES = dict()
    api.CODE_CHARS = "abc"
    api.CODE_LENGTH = 5
    assert api.lobby(token, query_string)[0] == 303


def test_lobby_invalid_code():
    party.PARTIES = dict()
    query_string = [("p", "invalid_party_code")]
    assert api.lobby(token, query_string) == (
        422,
        tuple(),
        b"<!DOCTYPE html><body><h1>Error: 422!!</h1><p>Unknown party code</p></body>",
    )


# POLL_START
def test_poll_start_valid_is_starting():
    default_party_setup()
    party.PARTIES["test_party_code"].status = "coding"
    assert api.poll_start(token, query_string) == (
        200,
        (("HX-Redirect", "/pages/coding.html"),),
        b"",
    )


def test_poll_start_valid_not_starting():
    default_party_setup()
    assert api.poll_start(token, query_string) == (200, tuple(), b"")


def test_poll_start_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.poll_start(token, query_string) == (
        400,
        tuple(),
        b"<!DOCTYPE html><body><h1>Error: 400!!</h1><p>You are not in any lobby!</p></body>",
    )


# POLL_ USERS
def test_poll_users_valid():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    response = api.poll_users(token, query_string)
    assert response[0] == 200
    assert response[2].decode().count("gladiator_") == 2


def test_poll_users_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.poll_users(token, query_string) == api.format_error(
        400, "You are not in any lobby!"
    )


# LOBBY_CTRL_PANEL
def test_lobby_ctrl_panel_valid_host():
    default_party_setup()
    response = api.lobby_ctrl_panel(token, query_string)
    assert response[0] == 200
    assert (
        response[2]
        != b'<p class="text-gray-600">Waiting for host to start the match...</p>'
    )


def test_lobby_ctrl_panel_valid_not_host():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    token = "test_token2"
    response = api.lobby_ctrl_panel(token, query_string)
    assert response[0] == 200
    assert (
        response[2]
        == b'<p class="text-gray-600">Waiting for host to start the match...</p>'
    )


def test_lobby_ctrl_panel_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.lobby_ctrl_panel(token, query_string) == api.format_error(
        400, "you are not in any lobby!"
    )


# CODING_CTRL_PANEL
def test_coding_ctrl_panel_valid_host():
    default_party_setup()
    response = api.coding_ctrl_panel(token, query_string)
    assert response[0] == 200
    assert len(response[2]) != 0


def test_coding_ctrl_panel_valid_not_host():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    token = "test_token2"
    response = api.coding_ctrl_panel(token, query_string)
    assert response[0] == 200
    assert len(response[2]) == 0


def test_coding_ctrl_panel_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.coding_ctrl_panel(token, query_string) == api.format_error(
        400, "you are not in any lobby!"
    )


# PROBLEM
def test_problem_valid():
    default_party_setup()
    party.PARTIES["test_party_code"].problem = [["", "this is my problem"]]
    response = api.problem(token, query_string)
    assert response[0] == 200
    assert response[2].decode().count("this is my problem") == 1


def test_problem_valid_no_problem():
    default_party_setup()
    response = api.problem(token, query_string)
    assert response[0] == 200
    assert response[2] == b"<h1>No Problem!</h1>"


def test_problem_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.problem(token, query_string) == api.format_error(
        400, "you are not in any lobby!"
    )


# POLL_END
def test_poll_end_valid_has_ended():
    default_party_setup()
    response = api.poll_end(token, query_string)
    assert response[0] == 200
    assert response[1][0] == ("HX-Redirect", "/pages/results.html")


def test_poll_end_valid_not_ended():
    default_party_setup()
    party.PARTIES["test_party_code"].status = "coding"
    response = api.poll_end(token, query_string)
    assert response[0] == 200
    assert len(response[1]) == 0


def test_poll_end_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.poll_end(token, query_string) == api.format_error(
        400, "you are not in any lobby!"
    )


# END
def test_end_valid_host():
    default_party_setup()
    assert api.end(token, query_string) == (
        303,
        (("location", "/pages/results.html"),),
        b"",
    )


def test_end_invalid_not_host():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    token = "test_token2"
    assert api.end(token, query_string) == api.format_error(
        400, "you are not the host!"
    )


def test_end_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.end(token, query_string) == api.format_error(
        400, "you are not in any lobby!"
    )


# RETURN_TO_LOBBY
def test_return_to_lobby_valid():
    default_party_setup()
    assert api.return_to_lobby(token, query_string) == (
        303,
        (("location", "/pages/lobby.html?p=test_party_code"),),
        b"",
    )


def test_return_to_lobby_invalid():
    default_party_setup()
    token = "invalid_test_token"
    assert api.return_to_lobby(token, query_string) == api.format_error(
        400, "you are not in any lobby!"
    )


# POLL STATS
def test_poll_without_lobby(tmp_path, monkeypatch):
    try:
        setup_api(tmp_path, monkeypatch)
        result = api.poll_stats("", "")
        assert result[0] == 400
    finally:
        os.close(test_pipe_reader)

def test_poll_with_lobby_in_progress(tmp_path, monkeypatch):
    try:
        test_db_manager.setup_db()
        party.init(test_db_manager.DB_PATH)
        default_party_setup()
        setup_api(tmp_path, monkeypatch)
        api.start(token, query_string)
        result = api.poll_stats(token, query_string)
        assert result[0] == 200
        assert "coding..." in result[2].decode()
    finally:
        os.close(test_pipe_reader)
        test_db_manager.remove_db()

# def test_poll_with_lobby_submit(tmp_path, monkeypatch):
#     try:
#         test_db_manager.setup_db()
#         party.init(test_db_manager.DB_PATH)
#         default_party_setup()
#         setup_api(tmp_path, monkeypatch)
#         api.start(token, query_string)
#         api.submit(token, "")
#         result = api.poll_stats(token, query_string)
#         assert result[0] == 200
#         assert "scoring..." in result[2].decode()
#     finally:
#         os.close(test_pipe_reader)
#         test_db_manager.remove_db()

def test_poll_with_lobby_ended(tmp_path, monkeypatch):
    try:
        test_db_manager.setup_db()
        party.init(test_db_manager.DB_PATH)
        default_party_setup()
        setup_api(tmp_path, monkeypatch)
        api.start(token, query_string)
        api.end(token, query_string)
        result = api.poll_stats(token, query_string)
        assert result[0] == 200
        assert "hx-get" not in result[2].decode()
    finally:
        os.close(test_pipe_reader)
        test_db_manager.remove_db()



# START
def test_start_valid():
    test_db_manager.setup_db()
    party.init(test_db_manager.DB_PATH)
    default_party_setup()
    assert api.start(token, query_string) == (
        303,
        (("location", "/pages/coding.html"),),
        b"",
    )
    test_db_manager.remove_db()


def test_start_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.start(token, query_string) == api.format_error(
        400, "You are not in any lobby!"
    )


def test_start_invalid_not_host():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    token = "test_token2"
    assert api.start(token, query_string) == api.format_error(
        403, "You are not the host!"
    )


def test_start_invalid_in_progress():
    default_party_setup()
    party.PARTIES["test_party_code"].status = "coding"
    assert api.start(token, query_string) == api.format_error(
        400, "The match is in progress."
    )


def test_start_invalid_database_issue():
    default_party_setup()
    assert api.start(token, query_string) == api.format_error(
        500, "Could not start match! This is probably because of a database issue..."
    )


# TODO
# SUBMIT
