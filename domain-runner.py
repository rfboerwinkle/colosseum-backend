#!/bin/python

import sys

import libvirt

if len(sys.argv) != 2:
  print("Usage: domain-runner.py FILE")
  exit()

xml = open(sys.argv[1]).read()

connection = libvirt.open()

def close():
  connection.close()
  exit()

# mem = connection.getFreeMemory()
# if mem < 2048 * 1024 * 1024:
#   print(f"""Not enough memory!
# {mem} / {2048*1024*1024} (B)
# It might work anyway. Only one way to find out ;)
# Continue anyway? [y/N]""")
#   response = input()
#   if response[:1].lower() != "y":
#     close()

success = False
next_action = "r"
while not success:
  if next_action == "k":
    try:
      for dom in connection.listAllDomains():
        dom.undefine()
      print("\nKilled everything, retrying.\n")
      next_action = "r"
    except:
      print("""
This is awkward. So much for "killing all the domains"...
If that error just said "cannot undefine transient domain", it's probably still
open and you have to close it.
q: quit  k: kill all domains  r: retry startup
Procede how? [Q/k/r]""")
      next_action = input()[:1].lower()

  elif next_action == "r":
    try:
      domain = connection.defineXML(xml)
      success = True
    except:
      print("""
...
Whoops
We can try killing all the domains and trying again.
CAUTION: This will do untold damage to ALL your vm's.
q: quit  k: kill all domains  r: retry startup
Procede how? [Q/k/r]""")
      next_action = input()[:1].lower()
  else:
    close()

print("Domain is ready.")
print("You can wait on this screen until you want to axe the domain.")
print("A blank input line will close the program/domain.")
print("Any other input will spawn an instance.")

if input():
  domain.createWithFlags(libvirt.VIR_DOMAIN_START_AUTODESTROY)
  input("Press ENTER to kill the domain.")

domain.undefine()
close()
