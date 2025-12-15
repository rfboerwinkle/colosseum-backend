import pytest
import party
# currently using 8.4.2 of pytest which isn't the latest?? Can't find/install 9.0.2

# PARTY INITALIZATION

# Is this something to test for? kinda not sure
# def test_party_inital_params():
#     test_party = party.Party()
#     assert len(test_party.gladiators) == 0
#     assert test_party.status == "not coding"
#     assert test_party.host == ""
#     assert test_party.problem == None

def test_party_invalid_params_passed():
  with pytest.raises(TypeError):
    _test_party = party.Party(1)

# __CONTAINS__
def test_contains_valid():
    test_party = party.Party()
    token = "first_token"
    test_party.add_gladiator(token)
    assert token in test_party

def test_contains_invalid():
    test_party = party.Party()
    assert "not_a_valid_token" not in test_party

def test_contains_invalid_type():
    test_party = party.Party()
    assert 123 not in test_party

# TODO: empty strings should probably not be considered a valid token...
# def test_contains_invalid_empty_string():
#     test_party = party.Party()
#     test_party.add_gladiator("")
#     if "" in test_party:
#         assert False
#     else:
#         assert True

# ADD_GLADIATOR
def test_add_gladiator_valid():
    test_party = party.Party()
    test_party.add_gladiator("test_token")
    assert "test_token" in test_party.gladiators

# not entirely sure how unexpected types passed in *should* be handled
def test_add_gladiator_unexpected_type():
    test_party = party.Party()
    with pytest.raises(TypeError):
        test_party.add_gladiator(123)

def test_add_gladiator_first_glad_is_host():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.add_gladiator("token2")
    assert test_party.host == "token1"

def test_add_gladiator_invalid_same_token():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.add_gladiator("token1")
    assert len(test_party.gladiators) == 1

def test_add_gladiator_unique_names():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.add_gladiator("token2")
    assert test_party.gladiators["token1"].name != test_party.gladiators["token2"].name

# TODO: check if gladiators have different names when added?

# DEL_GLADIATOR
def test_del_gladiator_valid():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.del_gladiator("token1")
    assert len(test_party.gladiators) == 0

def test_del_gladiator_invalid_token(capsys):
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.del_gladiator("token2")
    captured_output = capsys.readouterr()
    assert "glad not found." in captured_output.out
    assert len(test_party.gladiators) == 1

def test_del_gladiator_no_token(capsys):
    test_party = party.Party()
    test_party.del_gladiator("token2")
    captured_output = capsys.readouterr()
    assert "glad not found." in captured_output.out

def test_del_gladiator_host_handling1():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.add_gladiator("token2")
    test_party.del_gladiator("token1")
    assert test_party.host == "token2"

def test_del_gladiator_host_handling2():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.del_gladiator("token1")
    assert test_party.host == ""

# GET_GLADIATORS
# Honestly blanked on testing this one...
def test_get_gladiators_correct_type_output():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    glad_gen = test_party.get_gladiators()
    assert type(next(glad_gen)) is party.Gladiator

# END
def test_end():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.gladiators["token1"].status = "ready"
    test_party.end()
    assert test_party.status == "not coding"
    for g in test_party.gladiators:
        assert test_party.gladiators[g].status == "scored"
        assert len(test_party.gladiators[g].test_cases) == 0
        assert test_party.gladiators[g].status == "scored"

# START
# TODO: I couldn't do any testing because I need a working database
#  (and have no problems on hand to add to said database)

# SUBMIT
# TODO: possibly more error-catching tests since errors from submit could propagate into much worse
#  compared to the others erroring imo
def test_submit():
    test_party = party.Party()
    test_party.add_gladiator("token1")
    # What an awful way to do this I should totally fix it later
    test_party.problem = [[], [[b"test"]]]
    test_out = test_party.submit(b"code", "token1", b"body")
    assert type(test_out) is bytes
    assert test_party.gladiators["token1"].status == "submitted"

# GRADE
def test_grade_timeout(capsys):
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.gladiators["token1"].test_cases = [-1]
    test_party.grade(b"", b"\x02", b"token1-0")

    captured_output = capsys.readouterr()
    assert "(it timed out)" in captured_output.out
    assert test_party.gladiators["token1"].test_cases[0] == 0
    assert test_party.gladiators["token1"].score == 0.0
    assert test_party.gladiators["token1"].status == "scored"

def test_grade_passed(capsys):
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.gladiators["token1"].test_cases = [-1]
    test_party.problem = [[], [[b"", b"answer"]]]
    test_party.grade(b"answer", b"", b"token1-0")

    captured_output = capsys.readouterr()
    assert "(it passed)" in captured_output.out
    assert test_party.gladiators["token1"].test_cases[0] == 1
    assert test_party.gladiators["token1"].score == 1.0
    assert test_party.gladiators["token1"].status == "scored"

def test_grade_failed(capsys):
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.gladiators["token1"].test_cases = [-1]
    test_party.problem = [[], [[b"", b"answer"]]]
    test_party.grade(b"wrong_answer", b"", b"token1-0")

    captured_output = capsys.readouterr()
    assert "(it failed)" in captured_output.out
    assert test_party.gladiators["token1"].test_cases[0] == 0
    assert test_party.gladiators["token1"].score == 0.0
    assert test_party.gladiators["token1"].status == "scored"

def test_grade_correct_calculated_score(capsys):
    test_party = party.Party()
    test_party.add_gladiator("token1")
    test_party.gladiators["token1"].test_cases = [-1, 1]
    test_party.problem = [[], [[b"", b"answer"]]]
    test_party.grade(b"wrong_answer", b"", b"token1-0")

    captured_output = capsys.readouterr()
    assert "(it failed)" in captured_output.out
    assert test_party.gladiators["token1"].score == 0.5
