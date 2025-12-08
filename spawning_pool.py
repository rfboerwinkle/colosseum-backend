import os
import random
import shutil
import sys
import time

import libvirt

import lib_colosseum as lib
import xml_gen

class Broodling:
  # Pre-emptively cleans. Registers domain with libvirt
  def __init__(self, connection, suffix):
    lib.clean_tmp(suffix)
    self.suffix = suffix
    self.state = "something else"
    self.end_time = 0
    dom_xml = xml_gen.broodling(lib.MAIN_DISK, lib.get_out_file(suffix), suffix)
    self.domain = connection.defineXML(dom_xml)
    self.test_id = None

  # Boots the VM
  def start(self):
    lib.make_output(self.suffix)
    lib.make_input(self.suffix)
    lib.mount_input(self.suffix)
    self.domain.createWithFlags(libvirt.VIR_DOMAIN_START_AUTODESTROY)
    self.state = "turning on"

  def spin(self):
    if self.state == "ready":
      return b""
    elif self.state == "running":
      if self.end_time < time.monotonic():
        print(f"Broodling {self.suffix} timed out, turning off.")
        self.end()
        return b"\x00\x02\x00" + self.test_id + b"\x00"
      if self.domain.info()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
        lib.mount_output(self.suffix)
        file = os.path.join(lib.get_out_dir(self.suffix), "out.txt")
        f = open(file, "rb")
        out = f.read()
        f.close()
        lib.umount_output(self.suffix)
        lib.clean_tmp(self.suffix)
        print(f"Broodling {self.suffix} booting.")
        self.start()
        if 0 in out:
          # Test cases should NEVER have a null byte as an output.
          return b"\x00\x03\x00" + self.test_id + b"\x00"
        return out + b"\x00\x01\x00" + self.test_id + b"\x00"
      return b""
    elif self.state == "turning on":
      if self.domain.info()[0] == libvirt.VIR_DOMAIN_RUNNING:
        # This is so bad. Like, actually horrible.
        # I think it's pretty repeatable though.
        if b.domain.getCPUStats(-1, 0)[0]["cpu_time"] > 12000000000:
          print(f"Broodling {self.suffix} should be fully booted.")
          self.state = "ready"
      return b""
    elif self.state == "turning off":
      if self.domain.info()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
        print(f"Broodling {self.suffix} booting.")
        self.start()
      return b""
    else:
      print(f"Broodling {self.suffix} in unknown state: {self.state}")
      return None # This fails on purpose

  # Inserts the test disk, starting the auto-run inside the VM.
  def activate(self, code, test_input, timeout, test_id):
    print(f"Broodling {self.suffix} starting test: {test_id}")
    in_dir = lib.get_in_dir(self.suffix)
    f = open(os.path.join(in_dir, "main.py"), "w+b")
    f.write(code)
    f.close()
    f = open(os.path.join(in_dir, "input.txt"), "w+b")
    f.write(test_input)
    f.close()
    lib.umount_input(self.suffix)
    input_xml = lib.xml_input(self.suffix)
    self.domain.updateDeviceFlags(input_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)

    self.state = "running"
    self.end_time = time.monotonic() + timeout
    self.test_id = test_id

  def end(self):
    # Tries to kill VM gracefully. If that fails, pulls the plug.
    try:
      # This might fail if it's not running. That's okay.
      self.domain.destroy()
    except libvirt.libvirtError:
        pass
    lib.clean_tmp(self.suffix)
    self.state = "turning off"

  # After this is called, this instance should immediately be discarded.
  def dissolve(self):
    self.end()
    # Unregisters domain from libvirt
    self.domain.undefine()

conn = libvirt.open()
broodlings = []
test_pipe = os.open("test-pipe", os.O_RDONLY | os.O_NONBLOCK)
result_pipe = os.open("result-pipe", os.O_WRONLY)

try:
  for i in range(lib.POOL_SIZE):
    b = Broodling(conn, str(i))
    b.start()
    broodlings.append(b)

  incoming_jobs = []
  job_buffer = []
  data_buffer = b""
  while True:
    time.sleep(0.5)
    try:
      while True:
        # only read 10 bytes for testing purposes only, make it bigger eventually
        data = os.read(test_pipe, 10)
        oldi = 0
        for i,b in enumerate(data):
          if b == 0:
            data_buffer += data[oldi:i+1]
            oldi = i+1
            job_buffer.append(data_buffer[:-1])
            if len(job_buffer) == 4:
              job_buffer[2] = int(job_buffer[2])
              incoming_jobs.append(job_buffer)
              print("New job:", job_buffer[3])
              job_buffer = []
            data_buffer = b""
        if oldi != len(data):
          data_buffer += data[oldi:]
    except BlockingIOError:
      # test_pipe is non-blocking, so it will error if there is nothing to read.
      pass

    while incoming_jobs:
      for b in broodlings:
        if b.state == "ready":
          job = incoming_jobs.pop()
          b.activate(*job)
          break
      else:
        break

    for b in broodlings:
      print(f"suffix: {b.suffix}, int_state: {b.state}, ext_state:{b.domain.info()[0]}")
      out_data = b.spin()
      if len(out_data) != 0:
        os.write(result_pipe, out_data)

finally:
  print("Closing spawning_pool.main_loop for some reason. Cleaning up...")
  for b in broodlings:
    b.dissolve()

  for dom in conn.listAllDomains():
    print(f"Found a domain still defined after auto-cleanup: {dom.name()} Undefine it? [y/N]")
    if (input() + "n")[0] in "yY":
      dom.undefine()

  conn.close()
  os.close(test_pipe)
  os.close(result_pipe)
  print("...Finished cleanup.")
