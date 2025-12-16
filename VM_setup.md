# Overview

All of the VMs share a disk with different permissions. Only one of them should
be running at a time (except for the broodlings, which have the disk as
read-only).

`boot_installer.py INSTALL_IMAGE` is for installing. Boot order is
`creep_disk.img` and then the install image you select.

`boot_queen.py` is for editing the install in its final form. It has write
access to the disk.

`boot_broodling.py TEST_SCRIPT INPUT_FILE SUFFIX` is what will be spawned for each
submission. It has no write access to the disk. This script will read in
`TEST_SCRIPT` and `INPUT_FILE` and put them on the virtual disk before inserting
it into the broodling. `SUFFIX` is used to distinguish broodlings. Only needs to
be unique for running broodlings.

The versions of software in this file probably aren't necessary, but I included
them in case you were curious.

Note that `$` implies non-root user, and `#` implies root user.

# Install host machine

I installed the latest stable version of debian (12.9).

Install `virt-manager` (I have v4.1.0).

# Install source vm

Download a DVD install image. I have the Debian 12.9.0 DVD. It is net install,
but these VMs will not have a network card. Luckily, we only want the bare
minimum.

Open virt-manager (as root). You will need to locate / make a storage pool. This
allows QEMU to access your install image, `creep_disk.img`, and the temporary
drives:

1. Under `Name`, select `QEMU/KVM`

2. Edit -> Connection Details -> Storage

There should be a `default` pool. This is fine. Make note of the `Location`. I
will call it `LOCATION`

Create a raw img file to serve as the virtual hard drive, and a tmp directory to
house the io files for the broodlings:

`# truncate --size=2147483648 LOCATION/creep_disk.img`
`# chown libvirt-qemu:libvirt-qemu LOCATION/creep_disk.img`
`# mkdir LOCATION/tmp`
`# chown libvirt-qemu:libvirt-qemu LOCATION/tmp`

You will also have to move the install disk to LOCATION.

You will also need to add the following line to your `env.cfg` file:

`storage_dir=LOCATION`

Run the creep installer domain. Note the root permissions. Also note, this
should be the path to the DVD, not the virtual hard drive:

`# ./boot_installer.py PATH_TO_INSTALL_IMAGE`

You should be able to open it in `virt-manager` and then spawn an instance.

Now you should be in the Debian install screen (note that if you wait on this
screen for too long it will assume you are deaf and restart with speech
synthesis...)! I'll walk you through the install process, but some of it is
however you like. Buttons and proceding to the next menu is done with `ENTER`,
but checkboxes are selected with `SPACE`.

Note that if you want to re-do this process, you can press `c` on the GRUB menu
and then run `exit`. The BIOS will fall back to the install disk.

- `Install`
- `C - No localization`
- Select a location
- Select a country
- Select a keymap
- It shouldn't detect an ethernet card. Select `no ethernet card`
- There should be a big red screen here about `No network interfaces`. Select
  `Continue`. Fuck the internet.
- Hostname: `colosseum`
- Root password: `the beating heart of rome`
- Full name: `gladiator`
- Username: `gladiator`
- Password: `gladiator`
- Select a timezone
- Disk partitioning is where it gets exciting :D  Select `Manual`
- Select the 2.1 GB disk
- Create new empty partition table on this device? `Yes`
- Select the newly created `FREE SPACE`
- `Create a new partition`
- `2.1 GB`
- `Primary`
- The defaults should be good, so `Done setting up the partition`
- `Finish partitioning and write changes to disk`
- It will warn you about not having swap. We don't care. Do you want to return
  to the partitioning menu? `No`
- Write the changes to disks? `Yes`
- Scan extra installation media? `No`
- Depending on if you are using a netinst CD or not, it will put in varying
  amounts of effort into getting you to setup a network mirror / HTTP proxy. We
  don't care, as we don't have a network card, and only want a minimal base
  system.
- Participate in the package usage survey? `No` (no network device anyway)
- I selected `standard system utilities` because I wanted python3 (REMEMBER:
  select boxes with `SPACE`, then `ENTER` to go to the next screen)
- Install the GRUB boot loader to your primary drive? `Yes`
- Device for boot loader installation: `/dev/vda` (NOT `virtio-colosseum-out`)
- `Continue` to reboot.
- The boot order should be such that you don't have to remove the installation
  media. Just let it reboot and select `Debian GNU/Linux` (the default) in the
  GRUB menu.

Okay, now you should be able to login to root.

`boot_installer.py` automatically mounts all the scripts you need onto
`/dev/vdb`. Run the following:

`# mkdir mnt`
`# mount /dev/vdb mnt`
`# cd mnt/vm_setup`
`# bash setup.sh 'I am aware of the risks.'`

kudos to: https://andreafortuna.org/2019/06/26/automount-usb-devices-on-linux-u
sing-udev-and-systemd/

shutdown the vm (`# shutdown now`)

Remember when we were in the host machine?

Okay, now shut down the domain by pressing `Enter` on `boot_installer.py`.

# Check the broodling

You should be able to run the broodling with this command. `TEST_SCRIPT` is
whatever python script you want to run. `INPUT_FILE` will be piped to stdin.
`SUFFIX` is whatever unique string identifier you want for this broodling
instance, typically a number.

`# ./boot_broodling.py TEST_SCRIPT INPUT_FILE SUFFIX`

You should probably wait for the cpu usage to be zero for 5ish seconds (there
are 2 peaks) before you mount the input. This can be monitored with
`virt-manager`. Other than that, you should just be able to step through the
process without intervention. Don't `clean up the tmp files` at the end,
though. You will want to mount the output and check to make sure you got the
right output:

`# cd LOCATION/tmp`

`# mount -o loop out-[SUFFIX].img out-[SUFFIX]-dir`

`$ cat out-[SUFFIX]-dir/out.txt`

If you got the right output, congrats!! You've setup the vm disk properly!

