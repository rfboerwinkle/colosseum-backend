def queen(main_drive, output_drive):
  return f"""<domain type='kvm'>
  <name>queen</name>
  <memory unit='MiB'>2048</memory>
  <os>
    <type arch='x86_64' machine="q35">hvm</type>
  </os>
  <features>
    <acpi/><apic/>
  </features>
  <!-- TODO: set it to be a static time (just out of spite perhaps?) -->
  <clock offset="utc"/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <vcpu>1</vcpu>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <source file='{main_drive}'/>
      <target dev='vda' bus='virtio'/>
      <boot order="1"/>
    </disk>

    <disk type="file" device="cdrom">
      <target dev="sda" bus="sata"/>
      <boot order="2"/>
    </disk>

    <disk type="file" device="cdrom">
      <target dev="sdb"/>
      <serial>colosseum-in</serial>
    </disk>

    <disk type="file" device="disk">
      <target dev="vdb"/>
      <source file="{output_drive}"/>
      <serial>colosseum-out</serial>
    </disk>

    <console type="pty">
      <alias name='main-console'/>
    </console>

    <channel type="unix">
      <source mode="bind"/>
      <target type="virtio" name="org.qemu.guest_agent.0"/>
    </channel>
    <channel type="spicevmc">
      <target type="virtio" name="com.redhat.spice.0"/>
    </channel>
    <input type="tablet" bus="usb"/>
    <graphics type="spice" port="-1" tlsPort="-1" autoport="yes">
      <image compression="off"/>
    </graphics>
    <video>
      <model type="virtio"/>
    </video>
    <redirdev bus="usb" type="spicevmc"/>
    <redirdev bus="usb" type="spicevmc"/>

  </devices>
</domain>"""

def broodling(main_drive, output_drive, suffix):
  return f"""<domain type='kvm'>
  <name>broodling-{suffix}</name>
  <memory unit='MiB'>2048</memory>
  <os>
    <type arch='x86_64' machine="q35">hvm</type>
  </os>
  <features>
    <acpi/><apic/>
  </features>
  <!-- TODO: set it to be a static time (just out of spite perhaps?) -->
  <clock offset="utc"/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <vcpu>1</vcpu>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <source file='{main_drive}'/>
      <target dev='vda' bus='virtio'/>
      <boot order="1"/>
      <shareable/>
      <readonly/>
    </disk>

    <disk type="file" device="cdrom">
      <target dev="sda" bus="sata"/>
      <boot order="2"/>
    </disk>

    <disk type="file" device="cdrom">
      <target dev="sdb"/>
      <serial>colosseum-in</serial>
    </disk>

    <disk type="file" device="disk">
      <target dev="vdb"/>
      <source file="{output_drive}"/>
      <serial>colosseum-out</serial>
    </disk>

    <console type="pty">
      <alias name='main-console'/>
    </console>

    <channel type="unix">
      <source mode="bind"/>
      <target type="virtio" name="org.qemu.guest_agent.0"/>
    </channel>
    <channel type="spicevmc">
      <target type="virtio" name="com.redhat.spice.0"/>
    </channel>
    <input type="tablet" bus="usb"/>
    <graphics type="spice" port="-1" tlsPort="-1" autoport="yes">
      <image compression="off"/>
    </graphics>
    <video>
      <model type="virtio"/>
    </video>
    <redirdev bus="usb" type="spicevmc"/>
    <redirdev bus="usb" type="spicevmc"/>

  </devices>
</domain>"""

def installer(main_drive, output_drive, install_disk):
  return f"""<domain type='kvm'>
  <name>installer</name>
  <memory unit='MiB'>2048</memory>
  <os>
    <type arch='x86_64' machine="q35">hvm</type>
  </os>
  <features>
    <acpi/><apic/>
  </features>
  <!-- TODO: set it to be a static time (just out of spite perhaps?) -->
  <clock offset="utc"/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <vcpu>1</vcpu>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <source file='{main_drive}'/>
      <target dev='vda' bus='virtio'/>
      <boot order="1"/>
    </disk>

    <disk type="file" device="cdrom">
      <source file="{install_disk}"/>
      <target dev="sda" bus="sata"/>
      <boot order="2"/>
    </disk>

    <disk type="file" device="cdrom">
      <target dev="sdb"/>
      <serial>colosseum-in</serial>
    </disk>

    <disk type="file" device="disk">
      <target dev="vdb"/>
      <source file="{output_drive}"/>
      <serial>colosseum-out</serial>
    </disk>

    <console type="pty">
      <alias name='main-console'/>
    </console>

    <channel type="unix">
      <source mode="bind"/>
      <target type="virtio" name="org.qemu.guest_agent.0"/>
    </channel>
    <channel type="spicevmc">
      <target type="virtio" name="com.redhat.spice.0"/>
    </channel>
    <input type="tablet" bus="usb"/>
    <graphics type="spice" port="-1" tlsPort="-1" autoport="yes">
      <image compression="off"/>
    </graphics>
    <video>
      <model type="virtio"/>
    </video>
    <redirdev bus="usb" type="spicevmc"/>
    <redirdev bus="usb" type="spicevmc"/>

  </devices>
</domain>"""

