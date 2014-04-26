import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from queue import Queue

#------------------SETUP------------------#
output_pin = 7
input_pin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(output_pin,GPIO.OUT)
GPIO.setup(input_pin,GPIO.IN)
#------------------CLASS------------------#
class MorrowNIC(object):
	def __init__(self):
		self.previous_edge = datetime.now()
		self.current_edge = None
		self.last_pulse = None
		self.pulse_queue = Queue()
		self.bus_state = GPIO.input(input_pin)

		GPIO.add_event_detect(input_pin,GPIO.BOTH,callback=self.edgeFound)

	def edgeFound(self):
		self.current_edge = datetime.now()
		self.pulse_queue.put((self.bus_state,(self.current_edge-self.previous_edge).microseconds))
		self.previous_edge = self.current_edge
		self.bus_state = GPIO.input(input_pin)