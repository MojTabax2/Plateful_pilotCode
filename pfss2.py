from rpi_ws281x import PixelStrip, Color
import RPi.GPIO as GPIO
import time
import sys



LED_PIN_P = 10 #protein section light
LED_PIN_C = 21 #carb section light
LED_PIN_V = 12 #veggie secton light
lc_p = 24  # Number of LEDs in strip protin secton
lc_c = 12  # Number of LEDs in strip carb section
lc_v = 12  # Number of LEDs in strip veggie section
# Create PixelStrip objects for each LED strip
stripP = PixelStrip(lc_p, LED_PIN_P, 800000, 10, False, 100, 0)
stripC = PixelStrip(lc_c, LED_PIN_C, 800000, 10, False, 100, 0)
stripV = PixelStrip(lc_v, LED_PIN_V, 800000, 10, False, 100, 0)
# Initialize all strips
stripP.begin()
stripC.begin()
stripV.begin()


# Define helper function to set colors on a strip
def set_color(strip, color):
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
	strip.show()


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