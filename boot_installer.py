#!/bin/python3

print("UNTESTED")

import os
import shutil
import sys

import libvirt

import lib_colosseum as lib
import xml_gen

if len(sys.argv) != 2:
  print("Usage: boot_installer.py INSTALL_IMAGE")
  exit()

_,INSTALL_IMAGE = sys.argv
SUFFIX = "installer"

lib.clean_tmp(SUFFIX)
out_dir,out_file = lib.make_output(SUFFIX)
lib.mount_output(SUFFIX)
shutil.copytree(lib.VM_SETUP_DIR, out_dir)
lib.umount_output(SUFFIX)

dom_xml = xml_gen.installer(lib.MAIN_DISK, out_file, INSTALL_IMAGE)

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
