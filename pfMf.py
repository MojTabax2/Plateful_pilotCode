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
	'vegetable': ["/home/pft2/Desktop/pyCode/V1.mp3", "/home/pft2/Desktop/pyCode/V2.mp3", "/home/pft2/Desktop/pyCode/VE.mp3"],
	'protein': ["/home/pft2/Desktop/pyCode/P1.mp3", "/home/pft2/Desktop/pyCode/P2.mp3", "/home/pft2/Desktop/pyCode/P3.mp3", "/home/pft2/Desktop/pyCode/PE.mp3"],
	'carb': ["/home/pft2/Desktop/pyCode/C1.mp3", "/home/pft2/Desktop/pyCode/C2.mp3", "/home/pft2/Desktop/pyCode/C3.mp3"],
	'Coin': "/home/pft2/Desktop/pyCode/C.mp3"
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
	return sum(channel.value for _ in range(50)) / 50  # Average over 10 readings



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
		play_audio(random.choice(audio_files[section]))
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
	play_audio(audio_files['greeting'])
	#calibrated_values = [calibrate(ch) for ch in fsr_channels]


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
		
		if current_time - last_db_update >= 15:
			ref.set({'Protein': data_points_P, 'Vegetables': data_points_V, 'Carbs': data_points_C})
			last_db_update = current_time



		# Initiate sections at appropriate times
		if not section_states['Vegetables'] and current_time >= start_time and current_time <= start_time + 60:
			initiate_section('Vegetables')
			section_states['Vegetables'] = True
			section_new['Vegetables'] = True

		if not section_states['Protein'] and current_time >= protein_activation_time and current_time <= start_time + 240:
			initiate_section('Protein')
			section_states['Protein'] = True
			section_new['Protein'] = True

		if not section_states['Carbs'] and current_time >= carbs_activation_time and current_time <= start_time + 420:
			initiate_section('Carbs')
			section_states['Carbs'] = True
			section_new['Carbs'] = True



		# Workflow logic for interaction
		if section_states['Vegetables'] and section_new['Vegetables'] and not section_states['Protein'] and not section_states['Carbs'] and int(fsr_values[1]/100) != 0:
			if fsr_values[1]/100 == data_points_V[-1]/100:  # Vegetables section not used
				tlr('Vegetables', 'light_pulse')
				if int(fsr_values[0]/100) != 0 and fsr_values[0]/100 < data_points_P[-1]/100:
					play_audio(audio_files['vegetable'[2]])
					print("protein instead of v")
				elif int(fsr_values[2]/100) != 0 and fsr_values[2]/100 < data_points_C[-1]/100:
					tlr('carbs','light_B')
					play_audio(audio_files['vegetable'[2]])
					print("carbs instead of V")

			elif fsr_values[1]/100 < data_points_V[-1]/100:			
				play_audio(random.choice(audio_files['vegetable']))
				play_audio(audio_files['Coin'])
				print("1st time veggie")
				section_new['Vegetables'] = False

		
		if section_states['Protein'] and section_new['Protein'] and not section_states['Carbs'] and int(fsr_values[0]/100) != 0:
			if fsr_values[0]/100 == data_points_P[-1]/100:  # protein section not used
				tlr('Protein', 'light_pulse')
				if int(fsr_values[2]/100) != 0 and fsr_values[2]/100 < data_points_C[-1]/100:
					play_audio(audio_files['protein'[3]])
					print("carbs instead of p")
					
			elif fsr_values[0]/100 < data_points_P[-1]/100:				
				play_audio(random.choice(audio_files['protein']))
				play_audio(audio_files['Coin'])
				print("first bite p")
				section_new['Protein'] = False



		#activity
		if elapsed_time - last_checked > 120:
			last_checked = elapsed_time
			if fsr_values[0]/100 > (sum(data_points_P) / len(data_points_P))*0.9:
				play_audio(audio_files['protein'[3]])
				print("protein untouched")
			else:
				play_audio(random.choice(audio_files['protein']))
				play_audio(audio_files['Coin'])
			
			if fsr_values[1]/100 > (sum(data_points_V) / len(data_points_V))*0.9:
				play_audio(audio_files['vegetable'[2]])
				print("veggie untouched")
			else:
				play_audio(random.choice(audio_files['vegetable']))
				play_audio(audio_files['Coin'])
		



		# light off logic
		if elapsed_time > 300:
			if fsr_values[0]/100 < (data_points_P[-1]/100)*0.4:  # Turn off light when FSR drops below 40%
				tlr('Protein', 'light_off')
			if fsr_values[1]/100 < (data_points_V[-1]/100)*0.4:  # Turn off light when FSR drops below 40%
				tlr('Vegetables', 'light_off')
			if fsr_values[2]/100 < (data_points_C[-1]/100)*0.4:  # Turn off light when FSR drops below 40%
				tlr('Carbs', 'light_off')



		time.sleep(1)  # Wait 5 seconds before next reading

except KeyboardInterrupt:
	print("Script interrupted. Cleaning up GPIO...")

finally:
	tlr('Protein', 'light_off')
	tlr('Vegetables', 'light_off')
	tlr('Carbs', 'light_off')
	GPIO.cleanup()
	pygame.mixer.quit()
