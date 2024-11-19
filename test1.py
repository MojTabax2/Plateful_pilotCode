import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import RPi.GPIO as GPIO
import time
import pygame  # To play audio
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn


# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
# Initialize the ADS1115
ads = ADS1115(i2c)
# Create single-ended input channels for the three FSR sensors
fsr_channel_0 = AnalogIn(ads, 0)  # Channel A0
fsr_channel_1 = AnalogIn(ads, 1)  # Channel A1
fsr_channel_2 = AnalogIn(ads, 2)  # Channel A2


# Add this delay to ensure audio device is ready
time.sleep(5)
GPIO.setwarnings(False)


# Path to your downloaded service account key JSON file
cred = credentials.Certificate('/home/pft2/Desktop/pyCode/apiKey/platefultdb-firebase-adminsdk-y4pj8-55a9d1aabe.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://platefultdb-default-rtdb.firebaseio.com/'
})
# Reference to your device in the database
ref = db.reference('test/rpi/v2')


# GPIO Setup
#GPIO.setmode(GPIO.BOARD)  # Set to BCM mode to use GPIO numbering
BUTTON_PIN = 17         # Button connected to GPIO 17 (11 board)
LED_PIN = 23              # LED connected to Pin 16 (GPIO 23 BCM)
# Setup the GPIO pin as input with a pull-down resistor
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Setup the GPIO pin for the LED as output
GPIO.setup(LED_PIN, GPIO.OUT)


# Initialize variables
t1 = 0  # Initial value of t1
#last_state = GPIO.LOW  # To store the last state of the button


# Initialize pygame for audio playback
pygame.mixer.init()  # Initialize the mixer
audio_file = "/home/pft2/Desktop/pyCode/audio.mp3"  # Path to your audio file
a2 = "/home/pft2/Desktop/pyCode/t.mp3"  # Path to your audio file

# Calibration function to get a stable baseline value
def calibrate(channel):
    sum_readings = 0
    num_readings = 10  # Number of readings for averaging

    # Take multiple readings with a delay between each
    for _ in range(num_readings):
        sum_readings += channel.value  # Read analog value and add to sum
        time.sleep(0.1)  # Wait 100 ms between readings

    # Compute the average calibrated value
    avg_value = sum_readings / num_readings
    return avg_value  # Return the calibrated value


# Calibrate each sensor channel
print("Calibrating sensors...")
calibrated_fsr_0 = calibrate(fsr_channel_0)
calibrated_fsr_1 = calibrate(fsr_channel_1)
calibrated_fsr_2 = calibrate(fsr_channel_2)




try:
    while True:
        # Read the button state
        button_state = GPIO.input(BUTTON_PIN)
            
        # Read the values from each FSR sensor channel
        fsr_value_0 = int(fsr_channel_0.value - calibrated_fsr_0)
        fsr_value_1 = int(fsr_channel_1.value - calibrated_fsr_1)
        fsr_value_2 = int(fsr_channel_2.value - calibrated_fsr_2)
        # Print the adjusted ADC values to the serial
        print(f"{fsr_value_0}  {fsr_value_1}  {fsr_value_2}")
        time.sleep(0.1)
        
        # Detect a button press (transition from LOW to HIGH)
        if button_state == GPIO.LOW: #and last_state == GPIO.LOW:
            #t1 += 1.3  # Increment t1
            #ref.set(t1)  # Send the updated t1 value to Firebase
            #print(f"t1: {t1}")
            # Turn on the LED when the button is pressed
            GPIO.output(LED_PIN, GPIO.HIGH)
            
            # Calibrate each sensor channel
            print("Calibrating sensors...")
            calibrated_fsr_0 = calibrate(fsr_channel_0)
            calibrated_fsr_1 = calibrate(fsr_channel_1)
            calibrated_fsr_2 = calibrate(fsr_channel_2)
            time.sleep(0.5)
            
            pygame.mixer.music.load(a2)
            pygame.mixer.music.play()
            print("Played audio")
            # Play the audio file
            #time.sleep(1)
            
        else:
            # Turn off the LED when the button is released
            GPIO.output(LED_PIN, GPIO.LOW)

        # Update the last_state to the current state for the next loop
        #last_state = button_state
        
        # print("skipped")
        # Wait for a short time to debounce the button press (prevents bouncing)
        #time.sleep(0.1)  # Adjust the debounce time as necessary

except KeyboardInterrupt:
    print("Script interrupted. Cleaning up GPIO...")

finally:
    # Clean up GPIO pins when the script is done or interrupted
    GPIO.cleanup()
    pygame.mixer.quit()  # Clean up the audio mixer when done
