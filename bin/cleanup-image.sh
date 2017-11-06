#!/bin/bash
set -e
set -o pipefail

echo "Cleaning up machine before creating an image..."

sudo apt-get -y autoremove
sudo apt-get -y clean all
sudo find /var/cache -type f -exec rm -rf {} \;
sudo find /var/log -type f -exec rm -rf {} \;

rm -rf ~/.ssh/authorized_keys ~/.ansible
