#!/bin/python3

import os
import shutil
import sys

import libvirt

import lib_colosseum as lib
import xml_gen

if len(sys.argv) != 3:
  print("Usage: boot_broodling.py INPUT_FILE SUFFIX")
  exit()

_,INPUT_FILE,SUFFIX = sys.argv

lib.clean_tmp(SUFFIX)
out_dir,out_file = lib.make_output(SUFFIX)
in_dir,in_file = lib.make_input(SUFFIX)
dom_xml = xml_gen.broodling(lib.MAIN_DISK, out_file, SUFFIX)

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
  f = open(INPUT_FILE, "r")
  code = f.read()
  f.close()
  input_xml = lib.xml_input(SUFFIX)
  lib.mount_input(SUFFIX)
  f = open(os.path.join(in_dir, "main.py"), "w+")
  f.write(code)
  f.close()
  lib.umount_input(SUFFIX)
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
  input("Press enter to kill the broodling!")
  print()
  domain.undefine()
  conn.close()
