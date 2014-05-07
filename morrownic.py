import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from queue import Queue
from morrowutilities import charToBinaryDict,binaryToCharDict
import threading
from morrowstack import DatalinkLayer
import mac

#------------------SETUP------------------#
GPIO.setwarnings(False)
output_pin = 7
input_pin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(input_pin,GPIO.IN)
GPIO.setup(output_pin,GPIO.OUT)
GPIO.output(output_pin,GPIO.LOW)
GPIO.setup(output_pin,GPIO.IN)
#------------------CLASS------------------#
class MorrowNIC(object):
	def __init__(self,receive_queue,debug=False):
		"""
		Initializes the MorrowNet Virtual Network Interface Card
		"""
		self.debug = debug
		#----------------Identity Information----------------#
		self.mac = mac.my_mac
		self.mac_dict = {'router':'R'}
		self.ip = None
		if self.debug: print("Identity variables initialized")
		#---------------Transmission Variables---------------#
		self.pulse_duration = .01*1000000
		self.ack_wait = self.pulse_duration*100
		self.pulse_width = None
		self.previous_edge = datetime.now()
		self.current_edge = None
		if self.debug: print("Transmission variables initialized")
		#----------------Transmission Queues-----------------#
		self.receive_queue = receive_queue
		self.pulse_queue = Queue()
		self.send_queue = Queue()
		self.ack_send_queue = Queue()
		if self.debug: print("Transmission queues initialized")
		#----------------Transmission States-----------------#
		self.running = True
		self.bus_state = GPIO.input(input_pin)
		self.receiving_state = False
		self.last_ack_received = None
		if self.debug: print("Transmission states initialized")
		#--------------------NIC Threads---------------------#
		#----------Handle start and stop sequences-----------#
		GPIO.add_event_detect(input_pin,GPIO.BOTH,callback=self.edgeFound)
		self.send_thread = threading.Thread(target=self.sender)
		self.send_thread.start()
		if self.debug: 
			print("Threads started")
			print("MorrowNet Virtual Network Interface Card Initialized")
			print("Requesting IP address from router at MAC address: " + self.mac_dict['router'])
		if self.mac != self.mac_dict['router']:
			self.send_queue.put(DatalinkLayer(self.mac_dict['router'] + self.mac + "0000E0300E"))


	def edgeFound(self,pin):
		"""
		Callback function for GPIO edge detect
		"""
		#-------------------Measure Pulse--------------------#
		self.current_edge = datetime.now()
		delta = self.current_edge-self.previous_edge
		pulse = (self.bus_state,delta.seconds*1000000 + delta.microseconds)
		self.previous_edge = self.current_edge
		self.bus_state = GPIO.input(input_pin)

		#----------Handle start and stop sequences-----------#
		if pulse[0] and pulse[1] > 8*self.pulse_duration:
			if pulse[1] > 8*self.pulse_duration and pulse[1] < 10.5*self.pulse_duration:
				self.pulse_width = pulse[1]/9.0
				if receiving_state: self.pulse_queue = Queue()
				self.receiving_state = True
			elif pulse[1] >= 10.5*self.pulse_duration and pulse[1] < 13.5*self.pulse_duration:
				self.evaluateTransmission()
				if not receiving_state: self.pulse_queue = Queue()
				self.receiving_state = False
			return
		#--------------------Save Pulses---------------------#
		if self.receiving_state:
			self.pulse_queue.put(pulse)
			
	def evaluateTransmission(self):
		"""
		Translates pulses in the pulse queue into 
		characters and handles the result
		"""
		#-------------------Handle Pulses--------------------#
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
				length = 0
			transmission += str(pulse[0])*int(length)
		transmission = self.errorCorrect(transmission)
		#-------------------Handle Message--------------------#
		text = self.convertToText(transmission)
		if text == "":
			if self.debug: print("Received Error")
			return
		if self.debug: print("Received: " + text)
		if len(text) == 1:
			self.last_ack_received = text
		else:
			try:
				datalink = DatalinkLayer(text)
			except (AttributeError, IndexError, ValueError):
				pass
			else:
				self.updateMacDict(datalink)
				dest = datalink.getDestMAC()
				if dest == self.mac:
					if self.debug: print("Putting ack in queue: " + dest)
					self.ack_send_queue.put(dest)
					self.forward(datalink)

	def forward(self,datalink):
		"""
		adds the received transmission to the 
		receive_queue - created to be overwritten
		in the router class
		"""
		self.receive_queue.put(datalink.getPayload())

	def updateMacDict(self,datalink):
		"""
		allows the NIC to learn from transmissions
		and allows the NIC to set its IP address
		from a transmission sent by the router
		"""
		#-----------------------Unpack------------------------#
		dest_mac = datalink.getHeader(0)
		source_mac = datalink.getHeader(1)
		dest_ip = datalink.payload.getHeader(0)
		source_ip = datalink.payload.getHeader(1)
		#---------------------Assign IP-----------------------#
		if self.ip == None and self.mac == dest_mac:
			self.ip = dest_ip
			if self.debug: print("Self.ip: " + self.ip)
		#-------------Accumulate MAC information--------------#
		if dest_mac != self.mac_dict['router'] and dest_ip != '00':
			self.mac_dict[dest_ip] = dest_mac
		if source_mac != self.mac_dict['router'] and source_ip != '00':
			self.mac_dict[source_ip] = source_mac

	def errorCorrect(self,transmission): 
		"""
		this will ultimately correct errors
		in transmission
		"""
		return transmission

	def convertToText(self,transmission):
		"""
		converts received binary to text
		"""
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
		try:
			text = ''.join([binaryToCharDict[binary] for binary in sections])
		except:
			text = ""
		return text

	def convertToTransmission(self,text):
		"""
		converts text into binary ready for transmission
		"""
		while text[0] == " ":
			text = text[1:]
		text = text.upper()
		start_code = "1111111110"
		stop_code = "1111111111110"
		binary = ''.join([charToBinaryDict[char] for char in text])
		return start_code + binary + stop_code
	
	def transmit(self,trans):
		"""
		sends transmission over bus
		"""
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

	def sender(self):
		"""
		sending thread which checks the send queues,
		ensures that the bus is clear and then transmits
		the messages
		"""
		while self.running:
			#----------------------Send Acks----------------------#
			if not self.ack_send_queue.empty():
				transmission = self.convertToTransmission(self.ack_send_queue.get())
				sleep(self.pulse_duration*5/1000000)
				self.transmit(transmission)
				if self.debug: print("Sent ack")
			#-----------------Send Transmissions------------------#
			elif not self.send_queue.empty():
				difference = (datetime.now()-self.previous_edge)
				if (difference.seconds*1000000 + difference.microseconds) > self.ack_wait:
					datalink = self.send_queue.get()
					transmission = self.convertToTransmission(str(datalink))
					self.transmit(transmission)
					if self.debug: print("Sent transmission")
					#-----------------Handle Ack------------------#
					sleep(self.ack_wait/1000000)
					if self.last_ack_received == datalink.getDestMAC():
						if self.debug: print("Ack received: " + self.last_ack_received)
						self.last_ack_received = None
					else:
						self.send_queue.put(datalink)
			sleep((self.ack_wait/1000000)/4)

	def send(self,IP):
		"""
		function used by moros to send
		an IP object
		"""
		dest_ip = IP.getHeader(0)[1]
		if dest_ip in self.mac_dict:
			dest_mac = self.mac_dict[dest_ip]
		else:
			dest_mac = self.mac_dict['router']
		datalink = DatalinkLayer(IP,(dest_mac,self.mac))
		self.send_queue.put(datalink)

	def getIP(self):
		while not self.ip:
			time.sleep(.1)
		return self.ip

if __name__ == "__main__":
	s = .01
	receive_queue = Queue()
	nic = MorrowNIC(receive_queue)
	sleep(4)
	print(nic.mac)
	#nic.send_queue.put(DatalinkLayer("ININIIE08EEAPPMSG"))
	#nic.send_queue.put(DatalinkLayer("ININIIE08EEHINICK"))
	#nic.send_queue.put(DatalinkLayer("ININIIE08EEMORROW"))
	
