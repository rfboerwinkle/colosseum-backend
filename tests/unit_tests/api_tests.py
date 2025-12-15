import pytest
import api
import party

# INIT
# I was pretty lax with this test, just making sure everything get's assigned *something*
# TODO lots of dependency stuff here so maybe touch later...
# def test_api_inital_params():
#     CODE_CHARS = ""
#     CODE_LENGTH = 0
#     TEST_PIPE = None
#     TEST_MUTEX = None
#     RESULT_PIPE = None
#     RESULT_MUTEX = None

# FIND_PARTY
def test_find_party_valid():
    test_party = party.Party()
    test_party.add_gladiator("test_token")
    party.PARTIES["test_party_code"] = test_party
    print(api.find_party("test_token"))

    assert api.find_party("test_token") == "test_party_code"

def test_find_party_invalid():
    assert api.find_party("invalid_test_token") == ""


# FORMAT_ERROR
def test_format_error_valid():
    assert api.format_error(222, "test body") == (222, tuple(), b"<!DOCTYPE html><body><h1>Error: 222!!</h1><p>test body</p></body>")

# TODO:
# POLL RESULT PIPE
# LOBBY
# POLL_START
# POL_ USERS
# LOBBY_CTRL_PANEL
# CODING_CTRL_PANEL
# PROBLEM
# POLL_END
# END
# RETURN_TO_LOBBY
# POLL STATS
# START
# SUBMIT
