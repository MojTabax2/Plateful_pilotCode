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
from rpi_ws281x import PixelStrip, Color
#from pydub import AudioSegment
import io
import sys



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

# LED_PIN_P = 10 #protein section light
# LED_PIN_C = 12 #carb section light
# LED_PIN_V = 21 #veggie secton light
# lc_p = 24  # Number of LEDs in strip protin secton
# lc_c = 12  # Number of LEDs in strip carb section
# lc_v = 12  # Number of LEDs in strip veggie section
# # Create PixelStrip objects for each LED strip
# stripP = PixelStrip(lc_p, LED_PIN_P, 800000, 10, False, 255, 0)
# stripC = PixelStrip(lc_c, LED_PIN_C, 800000, 10, False, 255, 0)
# stripV = PixelStrip(lc_v, LED_PIN_V, 800000, 10, False, 255, 0)
# # Initialize all strips
# stripP.begin()
# stripC.begin()
# stripV.begin()

GPIO.setwarnings(False)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(LED_PIN_P, GPIO.OUT)
#GPIO.setup(LED_PIN_V, GPIO.OUT)
#GPIO.setup(LED_PIN_C, GPIO.OUT)
# Initialize audio
#pygame.mixer.pre_init(44100, -16, 2, 512)  # 44100 Hz, 16-bit stereo
#pygame.init()
pygame.mixer.init()

# File paths for audio
audio_files = {
	'greeting': "/home/pft2/Desktop/pyCode/audio.mp3",
	'vegetable': ["/home/pft2/Desktop/pyCode/audio2.mp3", "/home/pft2/Desktop/pyCode/audio3.mp3", "/home/pft2/Desktop/pyCode/audio4.mp3"],
	'protein': ["/home/pft2/Desktop/pyCode/audio5.mp3", "/home/pft2/Desktop/pyCode/audio6.mp3", "/home/pft2/Desktop/pyCode/audio7.mp3"],
	'carb': ["/home/pft2/Desktop/pyCode/audio8.mp3", "/home/pft2/Desktop/pyCode/audio9.mp3", "/home/pft2/Desktop/pyCode/audio10.mp3"],
	'warning': "/home/pft2/Desktop/pyCode/audio11.mp3"
}

# Helper function to play audio
def play_audio(file_path):
 	# audio = AudioSegment.from_file(file_path)
 	# audio = audio.set_frame_rate(44100)
 	# raw_audio = io.BytesIO()
 	# audio.export(raw_audio, format="mp3")

	pygame.mixer.music.load(file_path)
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy():
 		time.sleep(0.1)

# Helper functions
# def call_audio_script(file_path):
# 	subprocess.Popen(['python3', 'pfss.py', file_path])

# Calibration function
def calibrate(channel):
	return sum(channel.value for _ in range(10)) / 10  # Average over 10 readings

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

# # Define helper function to set colors on a strip
# def set_color(strip, color):
# 	for i in range(strip.numPixels()):
# 		strip.setPixelColor(i, color)
# 	strip.show()

# # Turn on lights for a specific section
# def light_up(section):
# 	# Implement GPIO control for light strips here based on section
# 	if section == 'Protein':
# 		set_color(stripP, Color(255, 0, 255))
# 	if section == 'Vegetables':
# 		set_color(stripV, Color(0, 255, 255))
# 	if section == 'Carbs':
# 		set_color(stripC, Color(255, 255, 0))

# def light_off(section):
# 	# Turn off the light strip for this section
# 	if section == 'Protein':
# 		set_color(stripP, Color(0, 0, 0))
# 	if section == 'Vegetables':
# 		set_color(stripV, Color(0, 0, 0))
# 	if section == 'Carbs':
# 		set_color(stripC, Color(0, 0, 0))


# def light_pulse(section):
# 	# pulse the light strip for this section
# 	end_time = time.time() + 5
# 	while time.time() < end_time:
# 		# Gradually increase brightness
# 		if section == 'Protein':
# 			for brightness in range(0, 256, 10):  # Adjust step for smoother transition
# 				stripP.setBrightness(brightness)
# 				set_color(stripP, Color(255, 0, 255))
# 				time.sleep(0.05)

# 			# Gradually decrease brightness
# 			for brightness in range(255, -1, -10):
# 				stripP.setBrightness(brightness)
# 				set_color(stripP, Color(255, 0, 255))
# 				time.sleep(0.05)

# 		if section == 'Vegetables':
# 			for brightness in range(0, 256, 10):  # Adjust step for smoother transition
# 				stripV.setBrightness(brightness)
# 				set_color(stripV, Color(0, 255, 255))
# 				time.sleep(0.05)

# 			# Gradually decrease brightness
# 			for brightness in range(255, -1, -10):
# 				stripV.setBrightness(brightness)
# 				set_color(stripV, Color(0, 255, 255))
# 				time.sleep(0.05)

# 		if section == 'Carbs':
# 			for brightness in range(0, 256, 10):  # Adjust step for smoother transition
# 				stripC.setBrightness(brightness)
# 				set_color(stripC, Color(255, 255, 0))
# 				time.sleep(0.05)

# 			# Gradually decrease brightness
# 			for brightness in range(255, -1, -10):
# 				stripC.setBrightness(brightness)
# 				set_color(stripC, Color(255, 255, 0))
# 				time.sleep(0.05)

# 	stripP.setBrightness(255)  # Reset brightness
# 	stripC.setBrightness(255)
# 	stripV.setBrightness(255)
# 	print(f"{section} light pulse.")
# def light_B():
# 	# make carbs brown
# 	set_color(stripC, Color(139, 69, 19))
# 	print("carb brown")

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
		# Process runs in the background; no need to wait for it to complete
		#stdout, stderr = process.communicate()
		print("LED reaction triggered in the background.")

		time.sleep(3)
		process.terminate()
	
	except subprocess.CalledProcessError as e:
		print(f"Error triggering LED reaction: {e}")
# def tlr(section, method):
# 	try:
# 		# Run the LED control script with `sudo`
# 		subprocess.run(
# 			['nohup','sudo','/home/pft2/myenv/bin/python3', '/home/pft2/Desktop/pyCode/pfss2.py', section, method],
# 			check=True,
# 			#timeout=3
# 		)
# 	except subprocess.CalledProcessError as e:
# 		print(f"Error triggering LED reaction: {e}")
# 	except subprocess.TimeoutExpired as e:
# 		print(f"light ON")
# 		print("\033[0m", end="")
# 		sys.stdout.flush()
# 	finally:
# 		# Reset terminal state after error
# 		print("\033[0m", end="")
# 		sys.stdout.flush()



# Initial section activation setup
def initiate_section(section):
	tlr(section, 'light_up')
	if section == 'Carbs':
		#play_audio(random.choice(audio_files[section]))
		print("carb audio played")

	print(f"{section} section activated.")

# Turn on initial sections at specific times
#initiate_section('Vegetables')  # Vegetables at 0 seconds
#section_states['Vegetables'] = True
protein_activation_time = start_time + 180  # 3 minutes
carbs_activation_time = start_time + 360  # 6 minutes

# Main loop
try:
	# Initial greeting audio
	play_audio(audio_files['greeting'])

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
		
		
		if current_time - last_db_update >= 20:
			ref.set({'Protein': data_points_P, 'Vegetables': data_points_V, 'Carbs': data_points_C})
			last_db_update = current_time

		# Initiate sections at appropriate times
		if not section_states['Vegetables'] and current_time >= start_time and current_time <= start_time + 60:
			initiate_section('Vegetables')
			section_states['Vegetables'] = True
			section_new['Vegetables'] = True

		# # waiting for the light board
		# # if not section_states['Protein'] and current_time >= protein_activation_time and current_time <= start_time + 240:
		# # 	initiate_section('Protein')
		# # 	section_states['Protein'] = True
		# # 	section_new['Protein'] = True

		# # if not section_states['Carbs'] and current_time >= carbs_activation_time and current_time <= start_time + 420:
		# # 	initiate_section('Carbs')
		# # 	section_states['Carbs'] = True
		# # 	section_new['Carbs'] = True

		# Workflow logic for interaction
		if section_states['Vegetables'] and section_new['Vegetables'] and not section_states['Protein'] and not section_states['Carbs'] and int(fsr_values[1]/100) != 0:
			if fsr_values[1]/100 == data_points_V[-1]/100:  # Vegetables section not used
				tlr('Vegetables', 'light_pulse')
				if int(fsr_values[0]/100) != 0 and fsr_values[0]/100 < data_points_P[-1]/100:
					#play_audio(random.choice(audio_files['Protein']))
					print("protein instead of v")
				elif int(fsr_values[2]/100) != 0 and fsr_values[2]/100 < data_points_C[-1]/100:
					#tlr('carbs','light_B')
					#play_audio(random.choice(audio_files['warning']))
					print("carbs nstead of V")

			elif fsr_values[1]/100 < data_points_V[-1]/100:			
				#play_audio(random.choice(audio_files['Vegetables']))
				print("1st time veggie")
				section_new['Vegetables'] = False

		# waiting for the light board
		# if section_states['Protein'] and section_new['Protein'] and not section_states['Carbs'] and int(fsr_values[0]/100) != 0:
		# 	if fsr_values[0]/100 == data_points_P[-1]/100:  # protein section not used
		# 		tlr('Protein', 'light_pulse')
		# 		if int(fsr_values[2]/100) != 0 and fsr_values[2]/100 < data_points_C[-1]/100:
		# 			#play_audio(random.choice(audio_files['Carbs']))
		# 			print("carbs nstead of p")
					
		# 	elif fsr_values[0]/100 < data_points_P[-1]/100:				
		# 		#play_audio(random.choice(audio_files['Protein']))
		# 		print("first bite p")
		# 		section_new['Protein'] = False


		#activity
		if elapsed_time - last_checked > 180:
			last_checked = elapsed_time
			if fsr_values[0]/100 > (sum(data_points_P) / len(data_points_P))*0.9:
				#play_audio(random.choice(audio_files['Protein']))
				print("protein untouched")
			if fsr_values[1]/100 > (sum(data_points_V) / len(data_points_V))*0.9:
				#play_audio(random.choice(audio_files['Vegetables']))
				print("veggie untouched")
								
		# light off logic
		if elapsed_time > 300:
			print("here")
			#if fsr_values[0]/100 < (data_points_P[-1]/100)*0.4:  # Turn off light when FSR drops below 40%
				#tlr('Protein', 'light_off')
			if fsr_values[1]/100 < (data_points_V[-1]/100)*0.4:  # Turn off light when FSR drops below 40%
				tlr('Vegetables', 'light_off')
			#if fsr_values[2]/100 < (data_points_C[-1]/100)*0.4:  # Turn off light when FSR drops below 40%
				#tlr('Carbs', 'light_off')

		time.sleep(1)  # Wait 5 seconds before next reading

except KeyboardInterrupt:
	print("Script interrupted. Cleaning up GPIO...")

finally:
	#tlr('Protein', 'light_off')
	#tlr('Vegetables', 'light_off')
	#tlr('Carbs', 'light_off')
	GPIO.cleanup()
	pygame.mixer.quit()
