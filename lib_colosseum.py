import os
import shutil
import subprocess
import sys

with open("env.cfg", "r") as f:
  for line in f:
    key,val = line.strip("\n\r").split("=", 1)
    if key == "wd":
      WD = val
    elif key == "pool-size":
      POOL_SIZE = int(val)
    elif key == "www":
      pass
    else:
      print(f"Unknown config key: {key}")

IO_TEMPLATE = os.path.join(WD, "io_template.img")
TMP_DIR = os.path.join(WD, "tmp")
MAIN_DISK = os.path.join(WD, "creep_disk.img")
VM_SETUP_DIR = os.path.join(WD, "vm_setup")

def get_out_dir(suffix):
  return os.path.join(TMP_DIR, f"out-{suffix}-dir")
def get_out_file(suffix):
  return os.path.join(TMP_DIR, f"out-{suffix}.img")
def get_in_dir(suffix):
  return os.path.join(TMP_DIR, f"in-{suffix}-dir")
def get_in_file(suffix):
  return os.path.join(TMP_DIR, f"in-{suffix}.img")

def clean_tmp(suffix):
  in_dir = get_in_dir(suffix)
  out_dir = get_out_dir(suffix)
  in_file = get_in_file(suffix)
  out_file = get_out_file(suffix)

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
    os.remove(in_file)
  except FileNotFoundError:
    pass
  try:
    os.remove(out_file)
  except FileNotFoundError:
    pass

def make_output(suffix):
  shutil.copyfile(IO_TEMPLATE, get_out_file(suffix))
  os.mkdir(get_out_dir(suffix))
def make_input(suffix):
  shutil.copyfile(IO_TEMPLATE, get_in_file(suffix))
  os.mkdir(get_in_dir(suffix))

def mount_output(suffix):
  out_dir = get_out_dir(suffix)
  out_file = get_out_file(suffix)
  # TODO: maybe make not a subprocess call?
  subprocess.run(["mount", "-o", "loop", out_file, out_dir])
def mount_input(suffix):
  in_dir = get_in_dir(suffix)
  in_file = get_in_file(suffix)
  # TODO: maybe make not a subprocess call?
  subprocess.run(["mount", "-o", "loop", in_file, in_dir])

def umount_output(suffix):
  out_dir = get_out_dir(suffix)
  subprocess.run(["umount", "-f", out_dir])
def umount_input(suffix):
  in_dir = get_in_dir(suffix)
  subprocess.run(["umount", "-f", in_dir])

def xml_input(suffix):
  in_file = get_in_file(suffix)
  return f"""
<disk type="file" device="cdrom">
  <source file="{in_file}"/>
  <target dev="sdb"/>
  <serial>colosseum-in</serial>
</disk>
"""
