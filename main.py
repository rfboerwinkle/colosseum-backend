from http import server
import json
import os
import queue
import random
import string
import threading

import party
import api

WWW = "./www"
WD = "./"
# CANNOT INCLUDE "-", SEE api.poll_result_pipe
CODE_CHARS = string.ascii_lowercase + string.digits
CODE_LENGTH = 5
PROBLEM_DATABASE = "problems.db"

with open("env.cfg", "r") as f:
  for line in f:
    key,val = line.strip("\n\r").split("=", 1)
    if key == "www":
      WWW = val
    elif key == "wd":
      WD = val
    elif key == "code_chars":
      CODE_CHARS = val
    elif key == "code_length":
      CODE_LENGTH = int(val)
    elif key == "problem_database":
      PROBLEM_DATABASE = val
    elif key == "pool-size":
      pass
    else:
      print(f"Unknown config key: {key}")

api.init(WWW, CODE_CHARS, CODE_LENGTH)
party.init(PROBLEM_DATABASE)

# CANNOT INCLUDE "-", SEE api.poll_result_pipe
TOKEN_CHARS = string.ascii_letters + string.digits
TOKEN_LENGTH = 30

job_queue = queue.Queue()

class RequestHandler(server.BaseHTTPRequestHandler):
  def do_GET(self):
    split_path = self.path.split("?")
    if len(split_path) == 1:
      p = split_path[0]
      q = ""
    elif len(split_path) == 2:
      p,q = split_path
    else:
      return self.send_error(400, "Bad path")

    p = tuple(p.strip("/").split("/"))
    token = ""
    if "cookie" in self.headers:
      token = self.headers["cookie"]
      print(f"cookie: {token}")
    else:
      print("no cookie :(")
    set_cookie = False
    if token == "":
      token = "".join(random.choices(TOKEN_CHARS, k=TOKEN_LENGTH))
      set_cookie = True

    query_string = []
    for query in q.split("&"):
      split_query = query.split("=")
      if len(split_query) == 1:
        query_string.append((split_query[0], ""))
      elif len(split_query) == 2:
        query_string.append(tuple(split_query))
      else:
        return self.send_error(400, "Bad Query string")
    query_string = tuple(query_string)

    if p == ("",):
      p = ("pages", "index.html")
      query_string = tuple()

    if p in api.GET_CALLS:
      ret,headers,payload = api.GET_CALLS[p](token, query_string)
    elif p in api.SERVABLE:
      ret = 200
      headers = tuple()
      payload = api.SERVABLE[p]
    else:
      ret = 404
      headers = tuple()
      payload = api.SERVABLE[("pages", "404.html")]

    self.send_response(ret)
    self.send_header("content-type", "text/html")
    if set_cookie:
      self.send_header("set-cookie", f"{token}; Path=/")
    for head in headers:
      self.send_header(head[0], head[1])
    self.end_headers()
    self.wfile.write(payload)
    return ret

  def do_POST(self):
    # We ignore everything after the question mark.
    # Don't send query strings in a POST!
    p = tuple(self.path.strip("/").split("?", 1)[0].split("/"))
    token = ""
    if "cookie" in self.headers:
      token = self.headers["cookie"]
      print(f"cookie: {token}")
    else:
      print("cookieless post :'(")
      return self.send_error(401, "No cookie / token!")

    try:
      length = int(self.headers["content-length"])
      body = self.rfile.read(length)
    except:
      return self.send_error(400, "Bad content / missing content-length header...")

    if p in api.POST_CALLS:
      # TODO: Maybe parse body before doing the post call?
      ret,headers,payload = api.POST_CALLS[p](token, body.decode())
    else:
      ret = 404
      headers = tuple()
      payload = api.SERVABLE[("pages", "404.html")]

    self.send_response(ret)
    self.send_header("content-type", "text/html")
    for head in headers:
      self.send_header(head[0], head[1])
    self.end_headers()
    self.wfile.write(payload)
    return ret

  # code = int
  # body = str
  # Body will be formatted into html and sent as an error.
  # Also prints the error.
  def send_error(code, body):
    print(f"ERROR {code}: {body}")
    self.send_response(code)
    self.send_header("content-type", "text/html")
    self.end_headers()
    self.wfile.write(f"<!DOCTYPE html><body><h1>Error: {code}!!</h1><p>{body}</p></body>".encode())
    return code

ser = server.ThreadingHTTPServer(("",8008), RequestHandler)

ser.serve_forever()
