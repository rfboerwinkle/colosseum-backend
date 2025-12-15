import os
import random
import threading
import time
import urllib

import party

SERVABLE = {}
CODE_CHARS = ""
CODE_LENGTH = 0
TEST_PIPE = None
TEST_MUTEX = None
RESULT_PIPE = None
RESULT_MUTEX = None
LAST_RESULT_POLL = 0
RESULT_BUFFER = []
RESULT_BYTE_BUFFER = b""

# This must be called before anything else in this file!!
def init(path, code_chars, code_length):
  global SERVABLE, CODE_CHARS, CODE_LENGTH, RESULT_PIPE, RESULT_MUTEX, TEST_PIPE, TEST_MUTEX
  CODE_CHARS = code_chars
  CODE_LENGTH = code_length
  for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
      filepath = os.path.join(dirpath, file)
      with open(filepath, "rb") as f:
        SERVABLE[tuple(os.path.relpath(filepath, path).split(os.sep))] = f.read()
  RESULT_PIPE = os.open("result_pipe", os.O_RDONLY | os.O_NONBLOCK)
  RESULT_MUTEX = threading.Lock()
  TEST_PIPE = os.open("test_pipe", os.O_WRONLY)
  TEST_MUTEX = threading.Lock()

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

# Polls the result pipe for information. I'm not entirely sure when it should be
# called. for right now, it is called at every poll_stats.
def poll_result_pipe():
  global LAST_RESULT_POLL, RESULT_BYTE_BUFFER, RESULT_BUFFER, RESULT_MUTEX
  with RESULT_MUTEX:
    cur_time = time.monotonic()
    if cur_time - LAST_RESULT_POLL > 1:
      LAST_RESULT_POLL = cur_time
      try:
        while True:
          # only read 10 bytes for testing purposes only, make it bigger eventually
          data = os.read(RESULT_PIPE, 10)
          oldi = 0
          for i,b in enumerate(data):
            if b == 0:
              RESULT_BYTE_BUFFER += data[oldi:i+1]
              oldi = i+1
              RESULT_BUFFER.append(RESULT_BYTE_BUFFER[:-1])
              if len(RESULT_BUFFER) == 3:
                code,token_n_test_case = RESULT_BUFFER[2].split(b"-", 1)
                code = code.decode()
                party.PARTIES[code].grade(RESULT_BUFFER[0], RESULT_BUFFER[1], token_n_test_case)
                RESULT_BUFFER = []
              RESULT_BYTE_BUFFER = b""
          if oldi != len(data):
            RESULT_BYTE_BUFFER += data[oldi:]
      except BlockingIOError:
        # test_pipe is non-blocking, so it will error if there is nothing to read.
        pass

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
    return (303, (("location", f"/pages/lobby.html?p={party_code}"),), b"")
  for p in party.PARTIES:
    if p == party_code:
      continue
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
  if party_code == "":
    return format_error(400, "You are not in any lobby!")
  p = party.PARTIES[party_code]
  if p.status == "coding" and p.gladiators[token].status == "ready":
    return (200, (("HX-Redirect", "/pages/coding.html"),), b"")
  else:
    return (200, tuple(), b"")

# GET
# TODO: remove "Player" header? that should be static
# TODO: indicate host
def poll_users(token, query_string):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "You are not in any lobby!")
  glads = party.PARTIES[party_code].get_gladiators()
  out = (
    b"<ul class=\"space-y-2 text-gray-700\"><li>"
    + b"</li><li>".join(glad.name.encode("utf-8") for glad in glads)
    + b"</li></ul>"
  )
  return (200, tuple(), out)

# GET
def lobby_ctrl_panel(token, query_string):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "you are not in any lobby!")
  if party.PARTIES[party_code].host == token:
    out = (
      b"<form action=\"/api/start\" method=\"post\">"
      + b"<input hidden type=\"text\" id=\"my-text\" name=\"my-text\">"
      + b"<input type=\"submit\" value=\"Start\" "
      + b"     class=\"px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 cursor-pointer\">"
      + b"</form>"
    )
    return (200, tuple(), out)
  else:
    out = (
      b"<p class=\"text-gray-600\">Waiting for host to start the match...</p>"
    )
    return (200, tuple(), out)

# GET
def coding_ctrl_panel(token, query_string):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "you are not in any lobby!")
  if party.PARTIES[party_code].host == token:
    out = (
      b"<a class=\"px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700\" "
      + b"href=\"/api/end\">"
      + b"End Match"
      + b"</a>"
    )
    return (200, tuple(), out)
  else:
    return (200, tuple(), b"")

# GET
def problem(token, query_string):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "you are not in any lobby!")
  prob = party.PARTIES[party_code].problem
  if prob == None:
    return (200, tuple(), b"<h1>No Problem!</h1>")
  else:
    return (200, tuple(), prob[0][1].encode("utf-8"))

# GET
def poll_end(token, query_string):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "you are not in any lobby!")
  if party.PARTIES[party_code].status == "not coding":
    # TODO: make redirects consistent
    return (200, (("HX-Redirect", "/pages/results.html"),), b"")
  else:
    return (200, tuple(), b"")

# GET
def end(token, query_string):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "you are not in any lobby!")
  p = party.PARTIES[party_code]
  if p.host == token:
    p.end()
    return (303, (("location", "/pages/results.html"),), b"")
  else:
    return format_error(400, "you are not the host!")

# GET
def return_to_lobby(token, query_string):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "you are not in any lobby!")
  return (303, (("location", f"/pages/lobby.html?p={party_code}"),), b"")

# GET
def poll_stats(token, query_string):
  poll_result_pipe()
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "You are not in any lobby!")

  should_poll = False
  for glad in party.PARTIES[party_code].get_gladiators():
    if glad.status != "scored":
      should_poll = True
      break

  if should_poll:
    polling_attributes = 'hx-get="/api/poll-stats" hx-trigger="every 1s" hx-target="#leaderboard" hx-swap="outerHTML"'
  else:
    polling_attributes = ""

  out = f"""
  <div id="leaderboard" class="bg-white rounded-xl shadow p-6" {polling_attributes}>
    <h2 class="text-lg font-semibold mb-4">Leaderboard</h2>
    <div class="space-y-2">
  """

  spinner_element = '<span class=\"inline-block h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin align-middle\" />'

  for glad in party.PARTIES[party_code].get_gladiators():
    out += f"""
    <div class="flex justify-between text-gray-700">
      <span>{glad.name}</span>
    """
    if glad.status == "ready":
      out += f'<span class="inline-flex items-center gap-2">coding...{spinner_element}</span>'
    elif glad.status == "submitted":
      out += f'<span class="inline-flex items-center gap-2">scoring...{spinner_element}</span>'
    elif glad.status == "scored":
      out += f'<span class="inline-flex items-center">{round(glad.score * 100)}</span>'
    out += "</div>"

  out += """
    </div>
  </div>
  """

  return (200, tuple(), out.encode())


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
  # Redirects to pages/coding if the game is not in the "not coding" state.
  # If the gladiator is not in any game, TODO
  ("api", "poll-start"): poll_start,
  # Returns a table of all the users in the current party.
  # If the gladiator is not in any party, throw an error.
  ("api", "poll-users"): poll_users,
  # Returns settings dialogue if you're the host
  # Returns nothing otherwise
  ("api", "lobby-ctrl-panel"): lobby_ctrl_panel,
  # Returns match setting dialogue if you're the host
  # Returns nothing otherwise
  ("api", "coding-ctrl-panel"): coding_ctrl_panel,
  # Gets the problem description.
  ("api", "problem"): problem,
  # Redirects the user to the results page if the party is in "not coding" state
  ("api", "poll-end"): poll_end,
  # Ends the match and redirects the user if you are the host
  # Returns an error if you are not the host
  ("api", "end"): end,
  # Returns the user back to the lobby of the current party
  ("api", "return-to-lobby"): return_to_lobby,
  # Returns a table of all the users' stats
  # If the gladiator is not in any party, throw an error.
  ("api", "poll-stats"): poll_stats,
}

# POST
def start(token, body):
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "You are not in any lobby!")
  p = party.PARTIES[party_code]
  if p.host != token:
    return format_error(403, "You are not the host!")
  if p.status == "coding":
    return format_error(400, "The match is in progress.")
  status = p.start()
  if not status:
    return format_error(500, "Could not start match! This is probably because of a database issue...")

  # you made it through all the checks, good job
  return (303, (("location", "/pages/coding.html"),), b"")

# POST
def submit(token, body):
  global TEST_MUTEX, TEST_PIPE
  print("Got this body:")
  print(body)
  party_code = find_party(token)
  if party_code == "":
    return format_error(400, "You are not in any lobby!")
  p = party.PARTIES[party_code]
  if p.status != "coding":
    return format_error(400, "Your party is not in a match right now!")
  if p.gladiators[token].status != "ready":
    return format_error(400, "You have already submitted!")
  good_body = urllib.parse.unquote_plus(body.split("=", 1)[1]).encode().replace(b"\x00", b"")
  submit_string = p.submit(party_code.encode(), token, good_body)
  with TEST_MUTEX:
    os.write(TEST_PIPE, submit_string)
  move_on = True
  for glad in p.get_gladiators():
    if glad.status == "ready":
      move_on = False
      break
  if move_on:
    p.end()
    print("Everyone Submitted!")
  return (303, (("location", "/pages/results.html"),), b"")

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
  # set-name
  # test
  # Runs code as a final submission, and redirect to results page.
  # TODO: right now it's just a placeholder. Actually make it do something
  ("api", "submit"): submit,
}
