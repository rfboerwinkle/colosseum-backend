#!/bin/sh

./clean.sh

name='io_template.img'
# 2MiB
truncate --size=2097152 $name
# I think this is a pretty good fs for this use case.
# NOTE: this uses a command in `/sbin`, but doesn't need root permissions.
/sbin/mkfs.ext2 -T default $name

mkfifo test_pipe result_pipe

echo "wd=$(pwd)" > env.cfg

echo 'Install complete (except for VM storage)'
