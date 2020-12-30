#!/bin/bash
if ! [ $(id -u) = 0 ]; then
    echo "You need to run this script as root!"
    exit 1
fi

echo "---------- Updating apt repository ----------"
apt update

echo "---------- Installing python3 ----------"
apt install python3 python3-pip python3-venv python3-distutils -y

echo "---------- Installing needed libraries ----------"
apt install git -y

echo "---------- Installing GPIO related libraries ----------"
pip3 install rpi_ws281x
pip3 install RPi.GPIO

git clone https://github.com/simonmonk/pi_analog.git
cd pi_analog
python3 setup.py install

cd ..

echo "---------- Cloning repository ----------"
git clone https://github.com/Esavojt/hodiny.git

cd hodiny
