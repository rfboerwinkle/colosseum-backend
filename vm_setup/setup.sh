# WARNING: THIS SHOULD ONLY BE USED IN A VM! AS SUCH, THERE IS NO SHEBANG.

if [ "$1" != 'I am aware of the risks.' ]; then
  echo 'Usage: bash vm-setup.sh '"'"'I am aware of the risks.'"'"
  exit 1
fi

# there might have been more...
apt purge -y isc-dhcp-client tasksel wget iproute2 nano openssh-client man-db python3-apt python3-debconf python3-pkg-resources python3-chardet python3-debian

apt autoremove --purge -y
apt clean

cp in_changed@.service /etc/systemd/system/

cp 99-in_changed.rules /etc/udev/rules.d/

echo -e '/dev/vdb\t/home/gladiator/out\text2\tdefaults\t0\t0' >> /etc/fstab

su gladiator

mkdir /home/gladiator/in
mkdir /home/gladiator/out

cp in_changed.sh /home/gladiator/
chmod 755 /home/gladiator/in_changed.sh

cp in_change_handler.sh /home/gladiator/
chmod 755 /home/gladiator/in_change_handler.sh

exit
exit
