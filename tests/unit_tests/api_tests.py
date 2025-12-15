import os

import pytest
import api
import party
import test_db_manager

# To maintain consistency across tests, PARTIES is cleared
# A party with code "test_party_code" is added with a single gladiator, "test_token"
def default_party_setup():
    party.PARTIES = dict()
    test_party = party.Party()
    test_party.add_gladiator("test_token")
    party.PARTIES["test_party_code"] = test_party

token = "test_token"
query_string = []

# TODO:
# INIT


# FIND_PARTY
def test_find_party_valid():
    default_party_setup()
    print(api.find_party(token))

    assert api.find_party(token) == "test_party_code"

def test_find_party_invalid():
    assert api.find_party("invalid_test_token") == ""


# FORMAT_ERROR
def test_format_error_valid():
    assert api.format_error(222, "test body") == (222, tuple(), b"<!DOCTYPE html><body><h1>Error: 222!!</h1><p>test body</p></body>")


# TODO:
# POLL RESULT PIPE


# LOBBY
def test_lobby_valid_code():
    api.SERVABLE[("pages", "lobby.html")] = ("pages", "index.html")
    default_party_setup()
    query_string = [("p", "test_party_code")]

    assert api.lobby(token, query_string) == (200, tuple(), ("pages", "index.html"))

# def test_lobby_glad_switch():
#     party.PARTIES = dict()
#     api.CODE_CHARS = "abc"
#     api.CODE_LENGTH = 5
#     test_party = party.Party()
#     party.PARTIES["test_party_code"] = test_party
#     test_party.add_gladiator("test_token")
#
#     token = "test_token"
#     query_string = []
    #
    # assert api.lobby(token, query_string)[0] == 303
    # # print(api.lobby(token, query_string))
    # for p in party.PARTIES:
    #     print(party.PARTIES[p].gladiators)
    # print("parties at: " + str(party.PARTIES))
    # assert api.find_party("test_token") != "test_party_code"
    # assert api.find_party("test_token") != ""

def test_lobby_creation():
    party.PARTIES = dict()
    api.CODE_CHARS = "abc"
    api.CODE_LENGTH = 5
    assert api.lobby(token, query_string)[0] == 303

def test_lobby_invalid_code():
    party.PARTIES = dict()
    query_string = [("p", "invalid_party_code")]
    assert api.lobby(token, query_string) == (422, tuple(), b"<!DOCTYPE html><body><h1>Error: 422!!</h1><p>Unknown party code</p></body>")


# POLL_START
def test_poll_start_valid_is_starting():
    default_party_setup()
    party.PARTIES["test_party_code"].status = "coding"
    assert api.poll_start(token, query_string) == (200, (("HX-Redirect", "/pages/coding.html"),), b"")

def test_poll_start_valid_not_starting():
    default_party_setup()
    assert api.poll_start(token, query_string) == (200, tuple(), b"")

def test_poll_start_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.poll_start(token, query_string) == (400, tuple(), b"<!DOCTYPE html><body><h1>Error: 400!!</h1><p>You are not in any lobby!</p></body>")


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
    assert api.poll_users(token, query_string) == api.format_error(400, "You are not in any lobby!")

# LOBBY_CTRL_PANEL
def test_lobby_ctrl_panel_valid_host():
    default_party_setup()
    response = api.lobby_ctrl_panel(token, query_string)
    assert response[0] == 200
    assert response[2] != b"<p class=\"text-gray-600\">Waiting for host to start the match...</p>"

def test_lobby_ctrl_panel_valid_not_host():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    token = "test_token2"
    response = api.lobby_ctrl_panel(token, query_string)
    assert response[0] == 200
    assert response[2] == b"<p class=\"text-gray-600\">Waiting for host to start the match...</p>"

def test_lobby_ctrl_panel_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.lobby_ctrl_panel(token, query_string) == api.format_error(400, "you are not in any lobby!")


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
    assert api.coding_ctrl_panel(token, query_string) == api.format_error(400, "you are not in any lobby!")


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
    assert api.problem(token, query_string) == api.format_error(400, "you are not in any lobby!")


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
    assert api.poll_end(token, query_string) == api.format_error(400, "you are not in any lobby!")


# END
def test_end_valid_host():
    default_party_setup()
    assert api.end(token, query_string) == (303, (("location", "/pages/results.html"),), b"")

def test_end_invalid_not_host():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    token = "test_token2"
    assert api.end(token, query_string) == api.format_error(400, "you are not the host!")

def test_end_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.end(token, query_string) == api.format_error(400, "you are not in any lobby!")


# RETURN_TO_LOBBY
def test_return_to_lobby_valid():
    default_party_setup()
    assert api.return_to_lobby(token, query_string) == (303, (("location", "/pages/lobby.html?p=test_party_code"),), b"")

def test_return_to_lobby_invalid():
    default_party_setup()
    token = "invalid_test_token"
    assert api.return_to_lobby(token, query_string) == api.format_error(400, "you are not in any lobby!")

# TODO: I just don't feel like touching this one rn...
# POLL STATS

# START
def test_start_valid():
    test_db_manager.setup_db()
    party.init(test_db_manager.DB_PATH)
    default_party_setup()
    assert api.start(token, query_string) == (303, (("location", "/pages/coding.html"),), b"")
    test_db_manager.remove_db()

def test_start_invalid_token():
    default_party_setup()
    token = "invalid_test_token"
    assert api.start(token, query_string) == api.format_error(400, "You are not in any lobby!")

def test_start_invalid_not_host():
    default_party_setup()
    party.PARTIES["test_party_code"].add_gladiator("test_token2")
    token = "test_token2"
    assert api.start(token, query_string) == api.format_error(403, "You are not the host!")

def test_start_invalid_in_progress():
    default_party_setup()
    party.PARTIES["test_party_code"].status = "coding"
    assert api.start(token, query_string) == api.format_error(400, "The match is in progress.")

def test_start_invalid_database_issue():
    default_party_setup()
    assert api.start(token, query_string) == api.format_error(500, "Could not start match! This is probably because of a database issue...")

# TODO:
# SUBMIT
