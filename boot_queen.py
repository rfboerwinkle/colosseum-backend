#!/bin/python3

print("UNTESTED")

import os
import shutil
import sys

import libvirt

import lib_colosseum as lib
import xml_gen

SUFFIX = "queen"

lib.clean_tmp(SUFFIX)
lib.make_output(SUFFIX)
out_file = lib.get_out_file(SUFFIX)
lib.make_input(SUFFIX)
dom_xml = xml_gen.broodling(lib.MAIN_DISK, out_file)

conn = libvirt.open()
domain = conn.defineXML(dom_xml)

try:
  print()
  print("Press Ctrl-c at any time to cancel.")
  print()
  print("Domain is ready.")
  print("Press enter to spawn an instance.")

  input()
  domain.createWithFlags(libvirt.VIR_DOMAIN_START_AUTODESTROY)

  print()
  print("Instance is ready.")
  print("Press enter to mount the input drive.")

  input()
  input_xml = lib.xml_input(SUFFIX)
  domain.updateDeviceFlags(input_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)

  print()
  print("Input mounted.")
  print("Press enter to clean up the tmp files and quit.")
  input()
  lib.clean_tmp(SUFFIX)
finally:
  print()
  print("If you just canceled or quit normally, all is chill.")
  print("If not, after you proceed the error will be printed.")
  input("Press enter to kill the queen (make sure the machine is powered off)!")
  print()
  domain.undefine()
  conn.close()
