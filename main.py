from http import server
import json
import os
import queue
import random
import string
import threading

WWW = "./www"
WD = "./"

with open("env.cfg", "r") as f:
    for line in f:
        key,val = line.strip("\n\r").split("=", 1)
        if key == "www":
            WWW = val
        elif key == "wd":
            WD = val
        else:
            print(f"Unkown config key: {key}")

SERVABLE = {}

for dirpath, dirnames, filenames in os.walk(WWW):
    for file in filenames:
        filepath = os.path.join(dirpath, file)
        with open(filepath, "rb") as f:
            SERVABLE[tuple(os.path.relpath(filepath, WWW).split(os.sep))] = f.read()

TOKEN_LENGTH = 30
TOKEN_CHARS = string.ascii_letters + string.digits

job_queue = queue.Queue()

API_CALLS = {
    ("pages", "index.html"):lambda _cookie,_query_string : SERVABLE[("pages", "index.html")],
    ("pages", "lobby.html"):lambda _cookie,_query_string : SERVABLE[("pages", "lobby.html")]
        }

class Game:
  def __init__(self):
    self.lock = threading.Lock()
    # token: (name, status, score)
    # token = str
    # name = str
    # status = "ready" | "submitted" | "scored"
    # score = int
    self.gladiators = dict()

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
          if new_token == glad:
            okay = False
            break

      self.gladiators[new_token] = (name, "ready", 0)
      self._update_all()
    return new_token

class RequestHandler(server.BaseHTTPRequestHandler):
  def do_GET(self):
    p = tuple(self.path.strip("/").split("/"))
    payload = "Uh oh! Empty Payload :("

    ret = 200
    if p in API_CALLS:
      # TODO: Update passed in value types if need be
      payload = API_CALLS[p](1,1)
    elif p in SERVABLE:
      payload = SERVABLE[p]
    else:
      payload = SERVABLE[("pages", "index.html")]
      ret = 404

    self.send_response(ret)
    self.send_header("content-type", "text/html")
    self.end_headers()
    self.wfile.write(payload)
    return ret
"""
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
"""
my_game = Game()

ser = server.ThreadingHTTPServer(("",8008), RequestHandler)

ser.serve_forever()
