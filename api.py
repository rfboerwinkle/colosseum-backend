import os
import random

import party

SERVABLE = {}
CODE_CHARS = ""
CODE_LENGTH = 0

# This must be called before anything else in this file!!
def init(path, code_chars, code_length):
  global SERVABLE, CODE_CHARS, CODE_LENGTH
  CODE_CHARS = code_chars
  CODE_LENGTH = code_length
  for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
      filepath = os.path.join(dirpath, file)
      with open(filepath, "rb") as f:
        SERVABLE[tuple(os.path.relpath(filepath, path).split(os.sep))] = f.read()

# helper function TODO: remove and replace with a data structure?
# Returns party code of a given gladiator's token.
# Returns "" if the gladiator isn't in a party.
def find_party(token):
  for p in party.PARTIES:
    if token in party.PARTIES[p]:
      return p
  else:
    return ""

# code = int
# body = str
# Body will be formatted into html and returned.
# Also prints the error.
def format_error(code, body):
  print(f"ERROR {code}: {body}")
  # The send_error function in main.py includes an additional header, but we
  # don't need it here because it gets added on later in the do_GET / do_POST
  # process.
  return (code, tuple(), f"<!DOCTYPE html><body><h1>Error: {code}!!</h1><p>{body}</p></body>".encode())

# TODO: timeout lobbies
# GET
def lobby(token, query_string):
  party_code = ""
  for key,value in query_string:
    if key == "p":
      party_code = value
  if party_code == "":
    party_code = "".join(random.choices(CODE_CHARS, k=CODE_LENGTH))
    while party_code in party.PARTIES:
      # TODO: Maintain DRY Principle
      # TODO: Dynamically expand party code length
      party_code = "".join(random.choices(CODE_CHARS, k=CODE_LENGTH))
    party.PARTIES[party_code] = party.Party()
    print(f"Made new party: {party_code}")
  for p in party.PARTIES:
    if party.PARTIES[p].del_gladiator(token):
      break
  if party_code in party.PARTIES:
    party.PARTIES[party_code].add_gladiator(token)
    return (200, tuple(), SERVABLE[("pages", "lobby.html")])
  else:
    return format_error(422, "Unknown party code")

# GET
def poll_start(token, query_string):
  party_code = find_party(token)
  if party_code != "":
    if party.PARTIES[party_code].status == "lobby":
      return (200, tuple(), b"")
    else:
      return (200, (("HX-Redirect", "/pages/coding.html"),), b"")
  else:
    return format_error(400, "You are not in any lobby!")

# GET_CALLS = { path: function(token, query_string) -> (code, headers, body), ... }
# path = (str, ...)
# token = str
# query_string = ((str, str), ...)
# code = int
# headers = ((str, str), ...)
# body = bytestr
GET_CALLS = {
  # TODO: is this important to put here? main.py should fall back to SERVABLE anyway
  # Serve the static index page
  ("pages", "index.html"): lambda _t,_q : (200, tuple(), SERVABLE[("pages", "index.html")]),
  # If the "l" query string is provided, join that lobby.
  # If it is not provided, make a new lobby.
  # If it is invalid, TODO
  ("pages", "lobby.html"): lobby,
  # Checks to see if the gladiator's game has been started.
  # Redirects to pages/coding if the game is not in the "lobby" state.
  # If the gladiator is not in any game, TODO
  ("api", "poll-start"): poll_start,
}

# POST
def start(token, body):
  party_code = find_party(token)
  if party_code != "":
    p = party.PARTIES[party_code]
    if p.host == token:
      if p.status == "lobby":
        p.status = "coding"
        return (303, (("location", "/pages/coding.html"),), b"")
      else:
        return format_error(400, "The match is in progress.")
    else:
      return format_error(403, "You are not the host!")
  else:
    return format_error(400, "You are not in any lobby!")

# POST_CALLS = { path: function(token, body) -> (code, headers, body), ... }
# path = (str, ...)
# token = str
# body = str
# code = int
# headers = ((str, str), ...)
# body = bytestr
POST_CALLS = {
  # Starts the gladiator's lobby and redirects to the coding page. TODO: Really redirect?
  # TODO: Setup match with parameters from the body.
  ("api", "start"): start,
}
