# Overview

You need a disk image (`$ truncate --size=2147483648 creep_disk.img`)

This disk will be used by all domains.

`python3 boot_[DOMAIN].py` to start a domain.

`boot_installer.py INSTALL_IMAGE` is for installing. Boot order is
`creep_disk.img` and then the install image you select. You can always
`'c' for a command-line`, and then `grub> exit` to fall back to the installer
(you should basically never have to wipe the disk image).

`boot_queen.py` is for editing the install in its final form. It has write
access to the disk.

`boot_broodling.py` is what will be spawned for each submission. It has no
write access to the disk.

The versions of software in this file probably aren't necessary, but I included
them in case you were curious.

# install host machine

I installed the latest stable version of debian (12.9).

Install `virt-manager` (I have v4.1.0).

# install source vm

create a raw img file to serve as the virtual hard drive:

`$ truncate --size=2147483648 creep_disk.img`

Download a DVD install image (offline). I have the Debian 12.9.0 DVD.

Run the creep installer domain. Note the root permissions. Also note, this
should be the path to the DVD, not the virtual hard drive. Also note, you
should probably have `virt-manager` open before you start:

`# ./boot_installer.py PATH_TO_INSTALL_IMAGE`

You should be able to spawn an instance and then open it up in `virt-manager`.
You might have to be quick about it? I'm not sure if it's time dependent lol :)

Now you should be in the Debian install screen! I'll walk you through the
install process, but some of it is however you like. Buttons and proceding to
the next menu is done with `ENTER`, but checkboxes are selected with `SPACE`.

## You should remove swap!!!!!

- `Install`
- `C - No localization`
- Select a location
- Select a country
- Select a keymap
- It shouldn't detect an ethernet card. Select `no ethernet card`
- There should be a big red screen here about `No network devices`. Select
  `Continue`. Fuck the internet.
- Hostname: `colosseum`
- Root password: `the beating heart of rome`
- Full name: `gladiator`
- Username: `gladiator`
- Password: `gladiator`
- Select a timezone
- This is where it gets exciting :D  Select `Guided - use entire disk`
- Select the only disk: `Virtual disk 1 (vda) - 2.1 GB Virtio Block Device`
- Select the only partitioning scheme: `All files in one partition [...]`
- `Finish partitioning and write changes to disk`
- Write the changes to disks? `Yes`
- Scan extra installation media? `No`
- Use a network mirror? `No` (no network device anyway)
- Participate in the package usage survey? `No` (no network device anyway)
- I selected `standard system utilities` because I wanted python3 (REMEMBER:
  select boxes with `SPACE`, then `ENTER` to go to the next screen)
- Install the GRUB boot loader to your primary drive? `Yes`
- Device for boot loader installation: `/dev/vda`
- `Continue`
- The boot order should be such that you don't have to remove the installation
  media. Just let it reboot and select `Debian GNU/Linux` (the default) in the
  GRUB menu.

Okay, now you should be able to login to root.

## CHECK TO SEE IF THE THING HAS ALREADY BEEN MOUNTED / ADDED TO FSTAB

## ENTER THE OUTPUT DRIVE AND RUN `setup.sh`

kudos to: https://andreafortuna.org/2019/06/26/automount-usb-devices-on-linux-using-udev-and-systemd/

shutdown the vm (`# shutdown now`)

Remember when we were in the host machine?

Okay, now shut down the domain by pressing `ENTER` on `boot_installer.py`.

# Check the broodling

You should be able to run the broodling with this command. `INPUT_FILE` is
whatever python script you want to run as sample input. `SUFFIX` whatever
unique string identifier you want for this broodling instance, typically a
number.

`# ./boot_broodling.py INPUT_FILE SUFFIX`

You should probably wait for the cpu usage to be zero for 5ish seconds (there
are 2 peaks) before you mount the input. This can be monitored with
`virt-manager`. Other than that, you should just be able to step through the
process without intervention. Don't `clean up the tmp files` at the end,
though. You will want to mount the output and check to make sure you got the
right output:

`$ cd tmp`

`# mount -o loop out-[SUFFIX]-dir out-[SUFFIX].img`

`$ cat out-[SUFFIX]-dir/out.txt`

If you got the right output, congrats!! You've setup the vm disk properly!

