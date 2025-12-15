#!/bin/sh

if [ "$ID_SERIAL_SHORT" = 'colosseum-in' ]; then
  /bin/systemctl start in_changed@$(basename $DEVNAME).service
fi
