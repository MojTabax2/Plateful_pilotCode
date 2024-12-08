from rpi_ws281x import PixelStrip, Color, ws
import RPi.GPIO as GPIO
import time
import sys



LED_PIN_PC = 12 #protein section light
LED_PIN_V = 10 #veggie secton light
lc_pc = 16  # Number of LEDs in strip protin secton
lc_v = 12  # Number of LEDs in strip veggie section
# Create PixelStrip objects for each LED strip
stripP = PixelStrip(lc_pc, LED_PIN_PC, 800000, 10, False, 255, 0,  ws.SK6812_STRIP_RGBW)
stripC = PixelStrip(lc_pc, LED_PIN_PC, 800000, 10, False, 255, 0,  ws.SK6812_STRIP_RGBW)
stripV = PixelStrip(lc_v, LED_PIN_V, 800000, 10, False, 255, 0,  ws.SK6812_STRIP_RGBW)
# Initialize all strips
stripP.begin()
stripC.begin()
stripV.begin()

global pcState
pcState = [Color(0, 0, 0)] * lc_pc

# Define helper function to set colors on a strip
def set_color(strip, color):
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


# Turn on lights for a specific section
def light_up(section):
	# Implement GPIO control for light strips here based on section
	if section == 'Protein':
		set_color(stripP, Color(255, 0, 0))
	elif section == 'Vegetables':
		set_color(stripV, Color(0, 255, 0))
	elif section == 'Carbs':
		set_color(stripC, Color(0, 0, 255))


def light_off(section):
	# Turn off the light strip for this section
	if section == 'Protein':
		set_color(stripP, Color(0, 0, 0))
	if section == 'Vegetables':
		set_color(stripV, Color(0, 0, 0))
	if section == 'Carbs':
		set_color(stripC, Color(0, 0, 0))

light_up('Vegetables')
light_up('Protein')
light_up('Carbs')
