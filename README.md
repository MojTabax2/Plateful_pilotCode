# Plateful_pilotCode
Python code for interactive plate

## Raspi setup:
- Run a following commands n the terminal:
``` shell
sudo apt update
sudo apt install python3-pip
pip install --upgrade pip
```
- Create and enter a vrtual env as follows:
``` shell
python3 -m venv myenv
source myenv/bin/activate
```


### Library installs
- Then install the following libraries:
``` shell
pip install firebase-admin
sudo apt-get install python3-rpi.gpio
pip install RPi.GPIO
pip install adafruit-blinka adafruit-circuitpython-ads1x15
pip install pygame
sudo apt-get install alsa-utils
sudo apt-get install libasound2-dev
pip install adafruit-circuitpython-neopixel
pip install rpi_ws281x
pip install pydub
```
- Do a reboot and then run this command
``` shell
source myenv/bin/activate
```


### Audio configuration
- Then run the following command
``` shell
sudo nano /boot/firmware/config.txt
```
- Add the following lines to the buttom of the file:
dtparam=audio=off
dtoverlay=i2s-mmap
dtoverlay=hifiberry-dac


### Sudo run configuration
- Then run:
``` shell
which python3
```
// This command will return an address path to you
- Run the following command to open the venv config file
``` shell
nano myenv/bin/activate
```
- Add the following line to the buttom of the file with the address path you got from the "which" command. This commad is added to aid with runing sudo inside the env while using the libraries. The LED strip managing libraries need to run on sudo:
alias supy='sudo THE_ADDRESS_PATH'


### How to run the code
- Now do another reboot and then activate the env again:
``` shell
source myenv/bin/activate
```
- Now "cd" to the path of your code
- Make sure the api-key is in the folder and your audio files are at the correct path
- run the code using:
``` shell
supy pfRpi2.py
```
