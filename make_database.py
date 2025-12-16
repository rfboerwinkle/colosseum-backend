#!/bin/python3

import database as d
import sys

if len(sys.argv) != 3:
  print("USAGE: make_database.py DATABASE_FILE PROBLEM_DIRECTORY")
  exit(1)

filename = sys.argv[1]
directory = sys.argv[2]


d.init_db(filename)
d.import_problems(filename, directory)
