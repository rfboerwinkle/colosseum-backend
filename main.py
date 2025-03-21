from http import server
import json
import os
import queue
import random
import string
import threading

SERVABLE = {
  "index.html": "index.html",
  "arena.html": "arena.html",
  "stands.html": "stands.html",
  "404.html": "404.html",
}
for file in SERVABLE:
  with open(os.path.join("www", file), "r") as f:
    SERVABLE[file] = f.read().encode()

TOKEN_LENGTH = 30
TOKEN_CHARS = string.ascii_letters + string.digits

job_queue = queue.Queue()

class Game:
  def __init__(self):
    self.lock = threading.Lock()
    # name: (token, status, score)
    # name = str
    # token = str
    # status = "ready" | "submitted" | "scored"
    # score = int
    self.gladiators = dict()
    # (current knowledge state, queue)
    self.subscribers = []

  def __contains__(self, key):
    with self.lock:
      return key in gladiators

  def add_gladiator(self, name):
    new_token = ""
    with self.lock:
      okay = False
      while not okay:
        new_token = "".join(random.choices(TOKEN_CHARS, k=TOKEN_LENGTH))
        okay = True
        for glad in self.gladiators:
          if new_token == self.gladiators[glad][0]:
            okay = False
            break

      self.gladiators[name] = (new_token, "ready", 0)
      self._update_all()
    return f"{{\"type\":\"token\",\"token\":\"{new_token}\"}}".encode()

  # DOES NOT LOCK!
  def _find_updates(self, cur_state):
    needs_updates = dict()
    for glad in self.gladiators:
      if (glad not in cur_state) \
         or (cur_state[glad] != self.gladiators[glad][1]):
        needs_updates[glad] = self.gladiators[glad][1:]

    if len(needs_updates) == 0:
      return b""
    else:
      return json.dumps({"type":"update", "content":needs_updates}).encode()

  def subscribe(self, cur_state, q):
    with self.lock:
      needs_updates = self._find_updates(cur_state)
      if len(needs_updates) != 0:
        q.put(needs_updates)
      else:
        self.subscribers.append((cur_state, q))

  # DOES NOT LOCK!
  def _update_all(self):
    new_subscribers = []
    for subscriber in self.subscribers:
      up = self._find_updates(subscriber[0])
      if up:
        subscriber[1].put(up)
      else:
        new_subscribers.append(subscriber)
    self.subscribers = new_subscribers

class RequestHandler(server.BaseHTTPRequestHandler):
  def do_GET(self):
    p = self.path.strip("/")

    ret = 200
    if p == "":
      p = "index.html"
    elif p not in SERVABLE:
      p = "404.html"
      ret = 404

    self.send_response(ret)
    self.send_header("content-type", "text/html")
    self.end_headers()
    self.wfile.write(SERVABLE[p])
    return ret

  def do_POST(self):
    path = self.path.strip("/")
    length = int(self.headers["content-length"])
    body = self.rfile.read(length)
    if path == "submit":
      job_queue.put(body)
      print(job_queue)
      # TODO: VM stuff here
      self.send_response(303)
      self.send_header("location", "stands.html")
      self.end_headers()
      return 303
    elif path == "join":
      ret = my_game.add_gladiator(body.decode())
      self.send_response(200)
      self.send_header("content-type", "application/json")
      self.end_headers()
      self.wfile.write(ret)
      return 200
    elif path == "statusquery":
      print(f"got statusquery\n{body}")
      q = queue.Queue()
      cur_state = json.loads(body.decode())
      my_game.subscribe(cur_state, q)
      ret = q.get()
      self.send_response(200)
      self.send_header("content-type", "application/json")
      self.end_headers()
      self.wfile.write(ret)
      print(f"\n\nreturned statusquery\n{ret}")
      return 200

my_game = Game()

ser = server.ThreadingHTTPServer(("",8008), RequestHandler)

ser.serve_forever()
