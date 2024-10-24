#!/bin/bash
set -o errexit

echo "trying to enter bootloader mode"

pigs modes  26 w    # Boot Pin
pigs w 26 1         # Press Boot
sleep 0.5
pigs modes 19 w     # Reset Pin
pigs w 19 0         # Press Reset
sleep 0.5
pigs w 19 1         # Release Reset
sleep 0.5
pigs w 26 0         # Release Boot  

echo ""
echo "Entered Bootloader Mode, Trying to flash MCU now!"

cd /home/cosi/klipper
make flash FLASH_DEVICE=0483:df11

echo ""
echo "finished flashing"