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
cred = credentials.Certificate("/home/pft2/Desktop/pyCode/apiKey/plateful-2e88e-firebase-adminsdk-r247n-d58f64e0c0.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://plateful-2e88e-default-rtdb.firebaseio.com/Pilot/D0/'})
PL = db.reference('Proteins')
VL = db.reference('Veggie')
CL = db.reference('Carbs')
Report = db.reference('Report')

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
	return sum(channel.value/100 for _ in range(10)) / 10  # Average over 10 readings

def isPos(i):
	return i>0


#light trigger	
def tlr(section, method):
	try:
		# Run the LED control script in the background using Popen
		process = subprocess.Popen(
			['sudo', '/home/pft2/myenv/bin/python3', '/home/pft2/Desktop/pyCode/pfss2.py', section, method],
			#stdout=subprocess.DEVNULL,  # Suppress output (you can redirect to a file if you want)
			#stderr=subprocess.DEVNULL,  # Suppress errors (you can redirect to a file if needed)
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
		play_audio(random.choice(audio_files["carb"]))
		
	print(f"{section} section activated.")



# Calibrate all sensors
calibrated_values = [calibrate(ch) for ch in fsr_channels]

# Data recording and timing setup
data_points_P = []
data_points_C = []
data_points_V = []
section_states = {'Protein': False, 'Vegetables': False, 'Carbs': False}
section_new = {'Protein': False, 'Vegetables': False, 'Carbs': False}

pReact = 0
vReact = 0


# Main loop
try:
	#tlr('Protein', 'light_off')
	#tlr('Vegetables', 'light_off')
	#tlr('Carbs', 'light_off')
	while True:
		# Read the button state
		button_state = GPIO.input(BUTTON_PIN)
		if button_state == GPIO.LOW:
			# Initial greeting audio
			play_audio(audio_files['greeting'])
			start_time = time.time()
			last_db_update = start_time
			last_db_saved = start_time
			# Turn on initial sections at specific times
			protein_activation_time = start_time + 120  # 2 minutes
			carbs_activation_time = start_time + 240  # 4 minutes


			while True:
				current_time = time.time()
				elapsed_time = current_time - start_time
				last_checked = 0
				

				# Read FSR sensors
				fsr_values = [int(ch.value/100 - cal) for ch, cal in zip(fsr_channels, calibrated_values)]
				print(f"Protein={fsr_values[1]}, Carbs={fsr_values[0]}, Vegetables={fsr_values[2]}")

				# Record data locally
				if (len(data_points_P) < 60 and current_time - last_db_saved >= 10) or len(data_points_P) < 2:
					data_points_P.append(fsr_values[1])
					data_points_C.append(fsr_values[0])
					data_points_V.append(fsr_values[2])
					last_db_saved = current_time
				
				# DB receives data
				if current_time - last_db_update >= 15:
					PL.set(data_points_P[-1])
					VL.set(data_points_V[-1])
					CL.set(data_points_C[-1])
					last_db_update = current_time



				# Initiate sections at appropriate times
				if not section_states['Vegetables'] and current_time >= start_time and current_time <= start_time + 60:
					initiate_section('Vegetables')
					section_states['Vegetables'] = True
					section_new['Vegetables'] = True

				if not section_states['Protein'] and current_time >= protein_activation_time and current_time <= start_time + 180:
					initiate_section('Protein')
					section_states['Protein'] = True
					section_new['Protein'] = True

				if not section_states['Carbs'] and current_time >= carbs_activation_time and current_time <= start_time + 300:
					initiate_section('Carbs')
					section_states['Carbs'] = True
					section_new['Carbs'] = True


				vDiff = int((data_points_V[-1] - fsr_values[2])/10)
				pDiff = int((data_points_P[-1] - fsr_values[1])/10)
				cDiff = int((data_points_C[-1] - fsr_values[0])/10)
				print("printing diff values:",vDiff,", ", pDiff, ", ", cDiff)
				# Workflow logic for interaction
				if section_new['Vegetables'] and not section_states['Protein'] and not section_states['Carbs']:
					if vDiff>=0:
						if vDiff > pDiff and vDiff > cDiff:
							if pDiff/10 >= 0 and cDiff/10 >=0:
								play_audio(random.choice(audio_files['vegetable']))
								play_audio(audio_files['Coin'])
								print("1st time veggie")
								section_new['Vegetables'] = False
						elif  vDiff < pDiff :
							play_audio(audio_files['vegetable'][2])
							print("protein instead of v")
							tlr('Vegetables', 'light_pulse')
						elif vDiff < cDiff:
							tlr('carbs','light_B')
							play_audio(audio_files['vegetable'][2])
							print("carbs instead of V")
							tlr('Vegetables', 'light_pulse')	


				
				if section_new['Protein'] and not section_states['Carbs']:
					if pDiff >=0:
						if pDiff > cDiff and cDiff/10 >=0:
							play_audio(random.choice(audio_files['protein']))
							play_audio(audio_files['Coin'])
							print("first bite pro")
							section_new['Protein'] = False
						elif pDiff < cDiff:
							play_audio(audio_files['protein'][3])
							print("carbs instead of p")
							tlr('Protein', 'light_pulse')
			

				#activity
				if (elapsed_time - last_checked) > 180:
					last_checked = elapsed_time
					if section_states['Protein']:
						if fsr_values[1] >= (sum(data_points_P) / len(data_points_P))*0.9:
							play_audio(audio_files['protein'][3])
							tlr('Protein', 'light_pulse')
							print("protein untouched")
						elif pReact <= 3:
							play_audio(random.choice(audio_files['protein']))
							pReact += 1
							play_audio(audio_files['Coin'])
					
					if section_states['Vegetables']:
						if fsr_values[2] >= (sum(data_points_V) / len(data_points_V))*0.9:
							play_audio(audio_files['vegetable'][2])
							tlr('Vegetables', 'light_pulse')
							print("veggie untouched")
						elif vReact <= 3:
							play_audio(random.choice(audio_files['vegetable']))
							vReact +=1
							play_audio(audio_files['Coin'])
				

				# light off logic
				if elapsed_time > 240:
					if fsr_values[1] < (data_points_P[1])*0.4:  # Turn off light when FSR drops below 40%
						tlr('Protein', 'light_off')
						section_states['Protein'] = False
					if fsr_values[2] < (data_points_V[1])*0.4:  # Turn off light when FSR drops below 40%
						tlr('Vegetables', 'light_off')
						section_states['Vegetables'] = False
					if fsr_values[0] < (data_points_C[1])*0.4:  # Turn off light when FSR drops below 40%
						tlr('Carbs', 'light_off')
						section_states['Carbs'] = False

					if section_states['Carbs'] == False and section_states['Vegetables'] == False and section_states['Protein'] == False:
						break



				time.sleep(1)  # Wait 5 seconds before next reading
				
			break

except KeyboardInterrupt:
	print("Script interrupted. Cleaning up GPIO...")

finally:
	rep = {
		"Protein": data_points_P,
		"Carbs": data_points_C,
		"Veggie": data_points_V
	}
	Report.set(rep)

	tlr('Protein', 'light_off')
	tlr('Vegetables', 'light_off')
	tlr('Carbs', 'light_off')
	GPIO.cleanup()
	pygame.mixer.quit()
