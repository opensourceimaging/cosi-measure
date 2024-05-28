# Software Getting Started

<!-- TOC -->

- [Software Getting Started](#software-getting-started)
    - [Installation](#installation)
        - [Download and Install Klipper](#download-and-install-klipper)
        - [Setting things up!](#setting-things-up)
        - [Config File](#config-file)
        - [Going into Bootloader Mode](#going-into-bootloader-mode)
        - [Flashing MCU and getting new Serial Port](#flashing-mcu-and-getting-new-serial-port)
    - [GUI](#gui)
    - [Commandline Interface](#commandline-interface)

<!-- /TOC -->


COSY Measure is using the open source 3D-printer firmware [klipper](https://www.klipper3d.org/). This document leads you through the installation. It´s assumed you have already installed [Raspberry-Pi-OS](https://www.raspberrypi.com/software/). We recommend the latest 64-bit Desktop version.

## Installation 

This Quick-Start-Guide is a short summary of https://www.klipper3d.org/Installation.html with some modifications for Rumba32 boards.

### 1. Download and Install Klipper

     git clone https://github.com/Klipper3d/klipper
     ./klipper/scripts/install-octopi.sh

Go to [backend/flash_mcu.sh](backend/flash_mcu.sh) and change the path in line 19 to the path of the repository above. For me line 19 is 

     19:  cd /home/cosi/klipper

### 2.1 Setting things up!

     cd klipper
     make menuconfig 

Opens a menu. Set
- Enable extra low-level configuration options
- Micro-controller Architecture (STMicroelectronics STM32)
- Processor model (STM32F446)
- Bootloader offset (32KiB bootloader)
- Clock Reference (12 MHz crystal)
- Communication interface (USB (on PA11/PA12))
- USB ids (doesnt matter. But choose something)
- no GPIO pins to set at startup ()

### 2.2 Config File

Get or write a ```printer.cfg```-file, here is mine: [backend/printer.cfg](backend/printer.cfg)

Save it as a file named "printer.cfg" in the home directory of the pi user (i.e. ```/home/cosi/printer.cfg```).

This file contains all machine configurations. Further reading: https://www.klipper3d.org/Installation.html#obtain-a-klipper-configuration-file

### 3. Going into Bootloader Mode

If not already done, install ```pigpio```for controlling the GPIO pins via the comand line: 

     sudo apt-get install pigpio
     sudo systemctl enable pigpiod
     sudo systemctl start pigpiod

The shell script ```backend/flash_mcu.sh``` will set the Rumba board into bootloader mode and eventually will try to flash the MCU. Execute 

     ./backend/flash_mcu.sh

to set the board into bootloader mode. Because it doesn´t know yet the usb-id of the microcontroller it will fail to flash - ignore that for now. Search the Device ID by executing 

     lsusb

This will show up something like

     Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
     Bus 001 Device 031: ID 0483:df11 STMicroelectronics STM Device in DFU Mode
     Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub

So in my installatiom ```0483:df11``` is the ID of the STM-chip of Rumba32. Change line 20 in ```backend/flash_mcu.sh``` to your device ID and save the file.

### 4. Flashing MCU and getting new Serial Port

Execute ```backend/flash_mcu.sh``` again. Now it shall flash the MCU. This will eventually look something like


     Downloading to address = 0x08008000, size = 29236
     Download	[=========================] 100%        29236 bytes
     Download done.
     File downloaded successfully
     Transitioning to dfuMANIFEST state
     dfu-util: can't detach
     Resetting USB to switch back to runtime mode
     cosi@raspberrypi:~/klipper $ 

Then search for serial ports by executing 

     ls /dev/serial/by-id/*

this will return something similar to 

     /dev/serial/by-id/usb-Klipper_stm32f446xx_280058000951363131343032-if00

Copy and paste it in ```/home/cosi/printer.cfg``` to your MCU serial definition:

     [mcu]
     serial: /dev/serial/by-id/usb-Klipper_stm32f446xx_280058000951363131343032-if00

Congratulations, now you´re done. Get a coffee. Enjoy.

## GUI

A GUI was developed in Python for COSI measure. Run 

     python main.py

and have a nice day enjoying your measurements.

You might need to install PyQT5 among some other things like Numy.


## Commandline Interface

Start the klipper service with executing

     sudo service klipper start

Klipper can be controlled via the following virtual serial port:

     /tmp/printer

Use 250000 Baud for communication. You can send G-code to this serial port and receive status information of the machine, refer to https://www.klipper3d.org/G-Codes.html. 

There are some custom g-code macros for disabling and enabling the drives without letting klipper loose it´s homing, for details see [printer.cfg](backend/printer.cfg) and [driver breakoutboard](../electronic-cabinet/Rumba32/Driver_BreakoutBoard/README.md). Use this commands only at standstill and never run a movement with disabled drives as this would eventually lead to false positioning.

Stop the klipper service by executing

     sudo service klipper stop