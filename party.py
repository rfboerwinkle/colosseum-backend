import random
import database

PARTIES = dict()

# TODO: token -> party mapping? we loop through parties looking for tokens a lot...

DATABASE_PATH = ""
def init(database_path):
  global DATABASE_PATH
  DATABASE_PATH = database_path

class Gladiator:
  def __init__(self, name="", status="ready", score=0):
    self.name = name
    self.status = status # "ready" | "submitted" | "scored"
    self.test_cases = []
    self.score = score

class Party:
  def __init__(self):
#    self.lock = threading.Lock()
    # { token: Gladiator, ... }
    # token = str
    self.gladiators = dict()
    # "not coding" | "coding"
    self.status = "not coding"
    # Host's token, or "" if there is no host.
    # The host is the first person in the lobby.
    # If the host leaves, TODO
    self.host = ""
    # If we are in the "coding" stage, guaranteed to be non-None
    # The format is exactly as returned by database.get_random
    self.problem = None

  # Returns True if this Gladiator is in this party (by token).
  def __contains__(self, token):
#    with self.lock:
    return token in self.gladiators

  # Adds a gladiator to this party.
  # Assigns a placeholder name until they assign their own.
  def add_gladiator(self, token):
    if token in self.gladiators:
      return
    if self.host == "":
      self.host = token
    num = -1
    okay = False
    while not okay:
      num += 1
      name = "gladiator_" + str(num)
      okay = True
      for g in self.gladiators:
        if self.gladiators[g].name == name:
          okay = False
          break
    print("glad was added. host is " + self.host)
    self.gladiators[token] = Gladiator(name, "ready", 0)

  # Removes a gladiator by their token.
  # Assigns a random host if the host left (or "" if there are no gladiators).
  def del_gladiator(self, token):
    if token in self.gladiators:
      del self.gladiators[token]
      if token == self.host:
        self.host = ""
        glads = tuple(self.gladiators.keys())
        if len(glads) != 0:
          self.host = random.choice(glads)
      print("glad was deleted. host is: " + self.host)
      return True
    else:
      print("glad not found. host is: " + self.host)
      return False

  # generates all of the gladiators' names
  def get_gladiators(self):
    for token in self.gladiators:
      yield self.gladiators[token]

  def end(self):
    self.status = "not coding"
    for glad in self.gladiators:
      if self.gladiators[glad].status == "ready":
        self.gladiators[glad].status = "scored"
        self.gladiators[glad].test_cases = []
        self.gladiators[glad].score = 0

  # Starts the round. Returns False on error, True on success.
  def start(self):
    try:
      self.problem = database.get_random(DATABASE_PATH)
    except:
      self.problem = None
      return False

    self.status = "coding"
    for glad in self.gladiators:
      self.gladiators[glad].status = "ready"
      self.gladiators[glad].test_cases = [-1 for x in range(len(self.problem[1]))]
      self.gladiators[glad].score = 0
    return True

  # This is kind of a hack, but we need the party's code for the test-id.
  # Currently, the party does not know its own code.
  # Hence, we pass in the code to this function.
  # `token` is the gladiator who is submitting, `body` is their submission.
  # Returns a bytestring ready to be sent to the spawning pool.
  # code: bytes
  # token: str
  # body: bytes
  def submit(self, code, token, body):
    out = b""
    for i in range(len(self.problem[1])):
      out += (
        body + b"\x00"
        + self.problem[1][i][0] + b"\x00"
        + "10".encode() + b"\x00" # TODO: make the timeout something
        + code + b"-" + token.encode() + b"-" + str(i).encode() + b"\x00"
      )
    self.gladiators[token].status = "submitted"
    return out

  # `output` is what the code returned.
  # `timeout` is whether the code timed out.
  # `token_n_test_case` is all of the test-id except for the party code.
  # output: bytes
  # timeout: bytes
  # token_n_test_case: bytes
  def grade(self, output, timeout, token_n_test_case):
    print(f"Party got output: {repr(output)}")
    token,test_case = token_n_test_case.split(b"-")
    token = token.decode()
    test_case = int(test_case.decode())
    g = self.gladiators[token]
    if timeout == b"\x02":
      print("  (it timed out)")
      g.test_cases[test_case] = 0
    else:
      if output == self.problem[1][test_case][1]:
        print("  (it passed)")
        g.test_cases[test_case] = 1
      else:
        print("  (it failed)")
        g.test_cases[test_case] = 0
    if all(s != -1 for s in g.test_cases):
      g.status = "scored"
      g.score = sum(g.test_cases) / len(g.test_cases)

