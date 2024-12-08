import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import RPi.GPIO as GPIO
import time
import pygame  # To play audio
import subprocess
import random  # For selecting random audio files
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn


# Initialize I2C bus and ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
fsr_channels = [AnalogIn(ads, i) for i in range(3)]  # 3 FSR sensors: Protein, Vegetables, Carbs

# Firebase setup
cred = credentials.Certificate('/home/pft2/Desktop/pyCode/apiKey/platefultdb-firebase-adminsdk-y4pj8-55a9d1aabe.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://platefultdb-default-rtdb.firebaseio.com/'})
ref = db.reference('test/rpi/v2')

# GPIO setup
BUTTON_PIN = 17
GPIO.setwarnings(False)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize audio
pygame.mixer.init()

# File paths for audio
audio_files = {
	'greeting': "/home/pft2/Desktop/pyCode/audio.mp3",
	'vegetable': ["/home/pft2/Desktop/pyCode/audio2.mp3", "/home/pft2/Desktop/pyCode/audio3.mp3", "/home/pft2/Desktop/pyCode/audio4.mp3"],
	'protein': ["/home/pft2/Desktop/pyCode/audio5.mp3", "/home/pft2/Desktop/pyCode/audio6.mp3", "/home/pft2/Desktop/pyCode/audio7.mp3"],
	'carb': ["/home/pft2/Desktop/pyCode/audio8.mp3", "/home/pft2/Desktop/pyCode/audio9.mp3", "/home/pft2/Desktop/pyCode/audio10.mp3"],
	'warning': "/home/pft2/Desktop/pyCode/audio11.mp3"
}


pygame.mixer.music.set_volume(1.0)
# Helper function to play audio
def play_audio(file_path):
	pygame.mixer.music.load(file_path)
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy():
 		time.sleep(0.1)



# Calibration function
def calibrate(channel):
	return sum(channel.value for _ in range(10)) / 10  # Average over 10 readings



#light trigger	
def tlr(section, method):
	try:
		# Run the LED control script in the background using Popen
		process = subprocess.Popen(
			['sudo', '/home/pft2/myenv/bin/python3', '/home/pft2/Desktop/pyCode/pfss2.py', section, method],
			stdout=subprocess.DEVNULL,  # Suppress output (you can redirect to a file if you want)
			stderr=subprocess.DEVNULL,  # Suppress errors (you can redirect to a file if needed)
			preexec_fn=lambda: None  # Ensures the process doesn't inherit terminal settings
		)
		print("LED reaction triggered in the background.")
		time.sleep(3)
		process.terminate()
		
	except subprocess.CalledProcessError as e:
		print(f"Error triggering LED reaction: {e}")



# Initial section activation setup
def initiate_section(section):
	tlr(section, 'light_up')
	if section == 'Carbs':
		#play_audio(random.choice(audio_files[section]))
		print("carb audio played")

	print(f"{section} section activated.")



# Calibrate all sensors
calibrated_values = [calibrate(ch) for ch in fsr_channels]

# Data recording and timing setup
data_points_P = []
data_points_C = []
data_points_V = []
start_time = time.time()
last_db_update = start_time
last_db_saved = start_time
section_states = {'Protein': False, 'Vegetables': False, 'Carbs': False}
section_new = {'Protein': False, 'Vegetables': False, 'Carbs': False}

# Turn on initial sections at specific times
protein_activation_time = start_time + 180  # 3 minutes
carbs_activation_time = start_time + 360  # 6 minutes



# Main loop
try:
	# Initial greeting audio
	#play_audio(audio_files['greeting'])
	calibrated_values = [calibrate(ch) for ch in fsr_channels]

	initiate_section('Vegetables')
	initiate_section('Protein')
	initiate_section('Carbs')

	while True:
		current_time = time.time()
		elapsed_time = current_time - start_time
		last_checked = 0
		
		# Read the button state
		button_state = GPIO.input(BUTTON_PIN)

		# Read FSR sensors
		fsr_values = [int(ch.value - cal) for ch, cal in zip(fsr_channels, calibrated_values)]
		print(f"Protein={fsr_values[0]}, Vegetables={fsr_values[1]}, Carbs={fsr_values[2]}")

		# Record data locally
		if len(data_points_P) < 60 and current_time - last_db_saved >= 10:
			data_points_P.append(fsr_values[0])
			data_points_V.append(fsr_values[1])
			data_points_C.append(fsr_values[2])
			last_db_saved = current_time




		time.sleep(1)  # Wait 5 seconds before next reading

except KeyboardInterrupt:
	print("Script interrupted. Cleaning up GPIO...")

finally:
	tlr('Protein', 'light_off')
	tlr('Vegetables', 'light_off')
	tlr('Carbs', 'light_off')
	GPIO.cleanup()
	pygame.mixer.quit()
