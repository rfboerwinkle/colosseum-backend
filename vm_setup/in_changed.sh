#!/bin/bash
mount -o ro "/dev/$1" /home/gladiator/in
python3 /home/gladiator/in/main.py > /home/gladiator/out/out.txt
shutdown now
