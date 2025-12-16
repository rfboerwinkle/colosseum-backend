from pytest_bdd import *
import requests


party_code = ""
host_session = requests.session()
user_session = requests.session()
user_invalid_session = requests.session()
SERVER_ADDRESS = "http://192.168.0.2:8008"
# SERVER_ADDRESS = "http://localhost:8008"


@scenario("join_lobby.feature", "A user wants to create a party")
def test_create_party():
    pass


@given("that I am on the index page", target_fixture="url")
def on_index_page():
    return host_session.get(f"{SERVER_ADDRESS}/pages/index.html")


@when("I press the 'Create New Party' button")
def make_new_party_request():
    global party_code
    r = host_session.get(
        f"{SERVER_ADDRESS}/pages/lobby.html", allow_redirects=True
    )
    party_code = r.url.split("p=")[1]
    print(party_code)


@then("a new party is created")
def get_party_size():
    r = host_session.get(f"{SERVER_ADDRESS}/api/poll-users")
    assert r.text.count("gladiator_") == 1


@then("I join the party as the host.")
def is_host():
    r = host_session.get(f"{SERVER_ADDRESS}/api/poll-users/lobby-control-panel")
    assert (
        r.text != '<p class="text-gray-600">Waiting for host to start the match...</p>'
    )


@scenario("join_lobby.feature", "A user want to join an existing party")
def test_join_party():
    pass


@given("that I am on the index page")
def on_index_page2():
    return user_session.get(f"{SERVER_ADDRESS}/pages/index.html")


@given("a host has created a party")
def host_created_party():
    # Reuse host_session
    pass


@given("I know the party code")
def know_party_code():
    pass


@when("I submit the party code")
def submit_party_code():
    r = user_session.get(
        f"{SERVER_ADDRESS}/pages/lobby.html", params={"p": party_code}
    )
    assert r.status_code == 200


@then("I join the party.")
def party_joined():
    r = user_session.get(f"{SERVER_ADDRESS}/api/poll-users")
    assert r.text.count("gladiator_") == 2


@scenario("join_lobby.feature", "A user types an incorrect party code")
def test_lobby_invalid():
    pass


@given("that I am on the index page")
def on_index_page3():
    return user_invalid_session.get(f"{SERVER_ADDRESS}/pages/index.html")


@when("I type in an invalid party code")
def get_invalid_code():
    global party_code
    party_code = "invalid"


@then("I am given an error.")
def error_given():
    r = user_invalid_session.get(
        f"{SERVER_ADDRESS}/pages/lobby.html", params={"p": party_code}
    )
    assert r.status_code == 422


@scenario("start_match.feature", "A host wants to start a match")
def test_start_match():
    pass


@given("that I am in a party")
def in_party():
    # Just reuse host_session
    pass


@given("I am the host")
def am_host():
    # Just reuse host_session
    pass


@when("I press the 'start match' button")
def press_start_match():
    response = host_session.post(
        f"{SERVER_ADDRESS}/api/start", allow_redirects=True
    )
    assert response.status_code == 200


@then("the party moves into the coding phase.")
def in_coding_phase():
    response = user_session.get(f"{SERVER_ADDRESS}/api/poll-start")
    assert response.headers.get("HX-Redirect") == "/pages/coding.html"


@scenario("host_end_match.feature", "Using end and poll-end api calls")
def test_end_match():
    pass


@given("the party is currently in a match")
def party_in_match():
    # Just reuse current lobby
    pass


@given("I am the host of the party")
def is_party_host():
    # Just reuse host_session
    pass


@when("I press the 'end match' button")
def press_end_match():
    host_session.get(f"{SERVER_ADDRESS}/api/end", allow_redirects=True)


@then("the match ends")
def match_ended():
    pass


@then("all gladiators are moved to the status page.")
def all_at_status_page():
    response = user_session.get(f"{SERVER_ADDRESS}/api/poll-end")
    assert response.headers.get("HX-Redirect") == "/pages/results.html"
    response = host_session.get(f"{SERVER_ADDRESS}/api/poll-end")
    assert response.headers.get("HX-Redirect") == "/pages/results.html"
