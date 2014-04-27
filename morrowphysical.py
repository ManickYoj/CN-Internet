import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from queue import Queue
from morrowglobals import charToBinaryDict,binaryToCharDict
import threading

#------------------SETUP------------------#

output_pin = 7
input_pin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(output_pin,GPIO.OUT)
GPIO.setup(input_pin,GPIO.IN)
GPIO.setwarnings(False)
#------------------CLASS------------------#
class MorrowNIC(object):
	def __init__(self):
		self.all_pulses = []
		self.MAC = 'A'
		
		self.pulse_duration = .01*1000000
		self.pulse_width = None

		self.previous_edge = datetime.now()
		self.current_edge = None
		
		self.receive_queue = Queue()
		self.pulse_queue = Queue()
		
		self.bus_state = GPIO.input(input_pin)
		self.receiving_state = False

		GPIO.add_event_detect(input_pin,GPIO.BOTH,callback=self.edgeFound)

		self.running = True
		self.send_queue = Queue()
		self.ack_queue = Queue()
		self.send_queue.put("B cat ran down the sidewalk")
		#self.send_queue.put("More stuff")
		self.ack_wait = self.pulse_duration*10
		self.send_thread = threading.Thread(target=self.send())
		self.send_thread.start()
		

	def edgeFound(self,pin):
		self.current_edge = datetime.now()
		delta = self.current_edge-self.previous_edge
		pulse = (self.bus_state,delta.seconds*1000000 + delta.microseconds)
		self.previous_edge = self.current_edge
		self.bus_state = GPIO.input(input_pin)
		self.all_pulses.append(pulse)
		if pulse[0] and pulse[1] >= 3.5*self.pulse_duration:
			if not self.receiving_state:
				self.pulse_width = pulse[1]/4.0
			if self.receiving_state:
				self.evaluateTransmission()
			self.receiving_state = not self.receiving_state
			return
		
		if self.receiving_state:
			self.pulse_queue.put(pulse)
			
	def evaluateTransmission(self):
		transmission = ""
		whitespace = self.pulse_queue.get()
		assert whitespace[0] == 0
		while not self.pulse_queue.empty():
			pulse = self.pulse_queue.get()
			length = pulse[1]
			if pulse[1] >= self.pulse_width*0.5 and pulse[1] <= self.pulse_width*2.0:
				length = 1
			elif pulse[1] > self.pulse_width*2.0 and pulse[1] <= self.pulse_width*4.0:
				length = 3
			elif pulse[1] > self.pulse_width*6.0 and pulse[1] <= self.pulse_width*8.0:
				length = 7
			else:
				print(length)
				length = 0
			transmission += str(pulse[0])*int(length)
		transmission = self.errorCorrect(transmission)
		#---TO BE EDITED---#
		text = self.convertToText(transmission)
		if len(text) == 1:
			self.ack_queue.put(text)
		else:
			datalink = Datalink(text)
			if datalink.dest_MAC == self.MAC:
				print("sending ack")
				self.ack_queue.put(datalink.source_MAC)
				self.receive_queue.put(datalink)
		print(text)

	def errorCorrect(self,transmission):
		return transmission

	def convertToText(self,transmission):
		sections = []
		words = transmission.split("0000000")
		for word in words:
			characters = word.split("000")
			chars = [char + "000" for char in characters]
			sections.extend(chars)
			sections.append("0000")
		while '000' in sections:
			sections.remove('000')
		if sections[-1] == "0000":
			sections = sections[:-1]
		#print(sections)
		text = ''.join([binaryToCharDict[binary] for binary in sections])
		return text

	def convertToTransmission(self,text):
		while text[0] == " ":
			text = text[1:]
		text = text.upper()
		marker_code = "11110"
		binary = ''.join([charToBinaryDict[char] for char in text])
		return marker_code + binary + marker_code
	
	def transmit(self,trans):
		GPIO.setup(output_pin,GPIO.OUT)
		for i in range(len(trans)):
			if trans[i] == '1':
				GPIO.output(output_pin,GPIO.HIGH)
				sleep(self.pulse_duration/1000000)
			else:
				GPIO.output(output_pin,GPIO.LOW)
				sleep(self.pulse_duration/1000000)
		GPIO.output(output_pin,GPIO.LOW)
		GPIO.setup(output_pin,GPIO.IN)

	def send(self):
		while self.running:
			if not self.ack_queue.empty():
				transmission = self.convertToTransmission(self.ack_queue.get())
				sleep(self.pulse_duration*5/1000000)
				self.transmit(transmission)
			elif not self.send_queue.empty():
				difference = (datetime.now()-self.previous_edge)
				if (difference.seconds*1000000 + difference.microseconds) > self.ack_wait:
					raw_transmission = self.send_queue.get()
					transmission = self.convertToTransmission(raw_transmission)
					self.transmit(transmission)
					sleep(self.ack_wait/1000000)
					if not self.ack_queue.empty():
						ack = self.ack_queue.get()
						print("ack received: " + ack)
					self.send_queue.put(raw_transmission)
			sleep((self.ack_wait/1000000)/4)
		
			
class Datalink(object):
	def __init__(self,transmission):
		self.dest_MAC = transmission[0]
		self.source_MAC = 'B'

if __name__ == "__main__":
	s = .01
	GPIO.output(7,GPIO.LOW)
	nic = MorrowNIC()
	
