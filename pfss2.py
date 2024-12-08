from rpi_ws281x import PixelStrip, Color, ws
import RPi.GPIO as GPIO
import time
import sys
import pickle
import os

# Define the file path for storing the state
STATE_FILE = "/home/pft2/Desktop/pyCode/pcState.pkl"

# Initialize the state if it doesn't already exist
def initialize_state():
    if not os.path.exists(STATE_FILE):
        default_state = [Color(0, 0, 0)] * lc_pc  # Default color is off
        save_state(default_state)
    return load_state()

# Save state to a file
def save_state(state):
    with open(STATE_FILE, "wb") as f:
        pickle.dump(state, f)

# Load state from a file
def load_state():
    with open(STATE_FILE, "rb") as f:
        return pickle.load(f)


LED_PIN_PC = 12 #protein section light
LED_PIN_V = 10 #veggie secton light
lc_pc = 16  # Number of LEDs in strip protin secton
lc_v = 12  # Number of LEDs in strip veggie section
# Create PixelStrip objects for each LED strip
stripP = PixelStrip(lc_pc, LED_PIN_PC, 800000, 10, False, 20, 0,  ws.SK6812_STRIP_RGBW)
stripC = PixelStrip(lc_pc, LED_PIN_PC, 800000, 10, False, 20, 0,  ws.SK6812_STRIP_RGBW)
stripV = PixelStrip(lc_v, LED_PIN_V, 800000, 10, False, 20, 0,  ws.SK6812_STRIP_RGBW)
# Initialize all strips
stripP.begin()
stripC.begin()
stripV.begin()

pcState = initialize_state()

# Define helper function to set colors on a strip
def set_color(strip, color):
	pcState = load_state()

	if strip == stripP:
		for i in range(0,8):
			pcState[i]=color
		for j, col in enumerate(pcState):
			strip.setPixelColor(j, col)
		print(pcState)
		strip.show()

	elif strip == stripC:
		for i in range(8,16):
			pcState[i]=color
		for j, col in enumerate(pcState):
			stripP.setPixelColor(j, col)
		print(pcState)
		stripP.show()

	elif strip == stripV:
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, color)
		strip.show()
		
	save_state(pcState)

# Turn on lights for a specific section
def light_up(section):
	# Implement GPIO control for light strips here based on section
	if section == 'Protein':
		set_color(stripP, Color(255, 0, 255))
	if section == 'Vegetables':
		set_color(stripV, Color(0, 255, 255))
	if section == 'Carbs':
		set_color(stripC, Color(255, 255, 0))


def light_off(section):
	# Turn off the light strip for this section
	if section == 'Protein':
		set_color(stripP, Color(0, 0, 0))
	if section == 'Vegetables':
		set_color(stripV, Color(0, 0, 0))
	if section == 'Carbs':
		set_color(stripC, Color(0, 0, 0))


def end():
	GPIO.cleanup()


def light_pulse(section):
	# pulse the light strip for this section
	end_time = time.time() + 5
	while time.time() < end_time:
		# Gradually increase brightness
		if section == 'Protein':
			for brightness in range(0, 256, 10):  # Adjust step for smoother transition
				stripP.setBrightness(brightness)
				set_color(stripP, Color(255, 0, 255))
				time.sleep(0.05)

			# Gradually decrease brightness
			for brightness in range(255, -1, -10):
				stripP.setBrightness(brightness)
				set_color(stripP, Color(255, 0, 255))
				time.sleep(0.05)

		if section == 'Vegetables':
			for brightness in range(0, 256, 10):  # Adjust step for smoother transition
				stripV.setBrightness(brightness)
				set_color(stripV, Color(0, 255, 255))
				time.sleep(0.05)

			# Gradually decrease brightness
			for brightness in range(255, -1, -10):
				stripV.setBrightness(brightness)
				set_color(stripV, Color(0, 255, 255))
				time.sleep(0.05)

		if section == 'Carbs':
			for brightness in range(0, 256, 10):  # Adjust step for smoother transition
				stripC.setBrightness(brightness)
				set_color(stripC, Color(255, 255, 0))
				time.sleep(0.05)

			# Gradually decrease brightness
			for brightness in range(255, -1, -10):
				stripC.setBrightness(brightness)
				set_color(stripC, Color(255, 255, 0))
				time.sleep(0.05)

	stripP.setBrightness(255)  # Reset brightness
	stripC.setBrightness(255)
	stripV.setBrightness(255)
	print(f"{section} light pulse.")

	
def light_B():
	# make carbs brown
	set_color(stripC, Color(139, 69, 19))
	print("carb brown")



def handle_action(section, method):
	if method == 'light_up':
		light_up(section)
	elif method == 'light_off':
		light_off(section)
	elif method == 'light_pulse':
		light_pulse(section)
	elif method == 'light_B':
		light_B()
	elif method == 'end':
		end()
	else:
		print(f"Unknown method: {method}")





if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: sudo python3 led_control.py <section> <method>")
		sys.exit(1)

	section = sys.argv[1]
	method = sys.argv[2]
	handle_action(section, method)
