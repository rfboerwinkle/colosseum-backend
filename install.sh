#!/bin/bash

./clean.sh

name='io-template.img'
# 2MiB
truncate --size=2097152 $name
# I think this is a pretty good fs for this use case.
# NOTE: this uses a command in `/sbin`, but doesn't need root permissions.
/sbin/mkfs.ext2 -T default $name

# maybe make this a tmpfs?
mkdir tmp

echo "wd=$(pwd)" > env.cfg
