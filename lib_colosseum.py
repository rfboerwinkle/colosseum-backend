import os
import shutil
import subprocess
import sys

with open("env.cfg", "r") as f:
  for line in f:
    key,val = line.strip("\n\r").split("=", 1)
    if key == "wd":
      WD = val
    else:
      print(f"Unknown config key: {key}")

IO_TEMPLATE = os.path.join(WD, "io-template.img")
TMP_DIR = os.path.join(WD, "tmp")
MAIN_DISK = os.path.join(WD, "creep-disk.img")
VM_SETUP_DIR = os.path.join(WD, "vm_setup")

def clean_tmp(suffix):
  in_dir = os.path.join(TMP_DIR, f"in-{suffix}-dir")
  out_dir = os.path.join(TMP_DIR, f"out-{suffix}-dir")
  in_file = os.path.join(TMP_DIR, f"in-{suffix}.img")
  out_file = os.path.join(TMP_DIR, f"out-{suffix}.img")

  # TODO: maybe make not a subprocess call?
  subprocess.run(["umount", "-f", in_dir])
  subprocess.run(["umount", "-f", out_dir])
  # I assume this is at least ok-practice if not best-practice?
  try:
    os.rmdir(in_dir)
  except FileNotFoundError:
    pass
  try:
    os.rmdir(out_dir)
  except FileNotFoundError:
    pass
  try:
    os.remove(os.path.join(TMP_DIR, f"in-{suffix}.img"))
  except FileNotFoundError:
    pass
  try:
    os.remove(os.path.join(TMP_DIR, f"out-{suffix}.img"))
  except FileNotFoundError:
    pass

def make_output(suffix):
  out_dir = os.path.join(TMP_DIR, f"out-{suffix}-dir")
  out_file = os.path.join(TMP_DIR, f"out-{suffix}.img")
  shutil.copyfile(IO_TEMPLATE, out_file)
  os.mkdir(out_dir)
  return (out_dir, out_file)

def make_input(suffix):
  in_dir = os.path.join(TMP_DIR, f"in-{suffix}-dir")
  in_file = os.path.join(TMP_DIR, f"in-{suffix}.img")
  shutil.copyfile(IO_TEMPLATE, in_file)
  os.mkdir(in_dir)
  return(in_dir, in_file)

def mount_input(suffix):
  in_dir = os.path.join(TMP_DIR, f"in-{suffix}-dir")
  in_file = os.path.join(TMP_DIR, f"in-{suffix}.img")
  # TODO: maybe make not a subprocess call?
  subprocess.run(["mount", "-o", "loop", in_file, in_dir])

def umount_input(suffix):
  in_dir = os.path.join(TMP_DIR, f"in-{suffix}-dir")
  subprocess.run(["umount", "-f", in_dir])

def xml_input(suffix):
  in_file = os.path.join(TMP_DIR, f"in-{suffix}.img")
  return f"""
<disk type="file" device="cdrom">
  <source file="{in_file}"/>
  <target dev="sdb"/>
  <serial>colosseum-in</serial>
</disk>
"""

