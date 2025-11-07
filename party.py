import random

PARTIES = dict()

# TODO: token -> party mapping? we loop through parties looking for tokens a lot...

class Party:
  def __init__(self):
#    self.lock = threading.Lock()
    # { token: (name, status, score), ... }
    # token = str
    # name = str
    # status = "ready" | "submitted" | "scored"
    # score = int
    self.gladiators = dict()
    # "lobby" | "coding" | "results"
    self.status = "lobby"
    # Host's token, or "" if there is no host.
    # The host is the first person in the lobby.
    # If the host leaves, TODO
    self.host = ""

  # Returns True if this Gladiator is in this party (by token).
  def __contains__(self, token):
#    with self.lock:
    return token in self.gladiators

  # Adds a gladiator to this party.
  # Assigns a placeholder name until they assign their own.
  def add_gladiator(self, token):
    if self.host == "":
      self.host = token
    num = -1
    okay = False
    while not okay:
      num += 1
      name = "gladiator_" + str(num)
      okay = True
      for g in self.gladiators:
        if g[0] == name:
          okay = False
          break
    self.gladiators[token] = (name, "ready", 0)

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
      return True
    else:
      return False

