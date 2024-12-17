# Plateful_pilotCode
Python code for interactive plate
This is a pilot version of the code and the workflow is as follows:
- Push of a button indicates start of a meal after the meal has been plated
- Initial weight (food data) is recorded
- Vegtable section is activated
  - If vegtable is eaten positive feedback of audio is played
  - Else the vegtable section light will blink and encoraging audio is played
- Next protein section is activated with similar workflow (2min into the meal)
- If carbs are consumed first in the meal the light will turn brown
- The carb section is activated after 4 min
- Every 3 min plate is assessed for change and positive or encoraging feedback is played
- If less than 40% of a section is left then the section will be deactivated

# Setup guide
if the device is already set-up go to [How to run the code](https://github.com/MojTabax2/Plateful_pilotCode/blob/main/README.md#how-to-run-the-code)



## Raspi setup:
- Run a following commands in the terminal:
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
```
dtparam=audio=off #it is ON by default just turn it off
dtparam=i2s=on 
dtoverlay=i2s-mmap
dtoverlay=hifiberry-dac
```



- Now do another reboot




## How to run the code
- Activate the env:
``` shell
source myenv/bin/activate
```
- "cd" to the path of your code (for our current rpi zero the path is Desktop/pyCode)
``` shell
cd Desktop/pyCode
```
- Make sure the api-key is in the folder and your audio files are at the correct path 
- run the code using:
``` shell
python3 main.py
```


## Technical Debt (TODO)
- Upgrade pilot workflow
- Configure database for better security or more intricate structure
- Add correct addresses and API keys to the main
