import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from queue import Queue
from morrowutilities import charToBinaryDict,binaryToCharDict
import threading
from morrowstack import DatalinkLayer, IPLayer
import mac
from morrownic import MorrowNIC
import random
import socket as s

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
class Router(MorrowNIC):
	"""
	Routers transmissions accross ethernet and MorrowNet
	Threads:
		Edge Detect (MorrowNet Receiving) - inherited from MorrowNIC
		Sender (MorrowNet Sending) - inherited from MorrowNIC
		routeEthernetToMorse - Eth to MorrowNet conversion
		routeMorseToEthernet - MorrowNet to Eth conversion and IP address assignment
	"""
	router_eth_ip = {"I":"192.168.100.73",
			"E":"192.168.100.50",
			"T":"192.168.100.84",
			"R":"192.168.100.82"
		    }
	socket, AF_INET, SOCK_DGRAM, timeout = s.socket, s.AF_INET, s.SOCK_DGRAM, s.timeout

	def __init__(self,verbose=True):
		"""
		Initializes router system
		"""
		self.verbose = verbose
		if self.verbose: print("Commencing router initialization")
		#--------------Initializes Real Socket---------------#
		self.Router_Address = ("10.26.8.23",5073)
		self.socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
		self.socket.bind(self.Router_Address)
		self.socket.settimeout(2.0)
		if self.verbose: print("Ethernet socket initialized")
		#------------Extends Itentity Information------------#
		self.group = mac.my_group
		self.ip = '00'
		self.mac = 'R'
		self.registry = {}
		if self.verbose: print("Identity Information Extended")
		#------------------Initializes NIC-------------------#
		receive_queue = Queue()
		super(Router,self).__init__(receive_queue)
		if self.verbose: print("MorrowNet Virtual Network Interface Card initialized")
		#---------------Starts Routing Threads---------------#
		self.E2M = threading.Thread(target=self.routeEthernetToMorse)
		self.M2E = threading.Thread(target=self.routeMorseToEthernet)
		self.E2M.start()
		self.M2E.start()
		if self.verbose: print("Routing threads started")
		if self.verbose: print("Initialization Complete")

	def forward(self,datalink):
		"""
		NIC file forwards transmission as IPLayer objects
		but router needs DatalinkLayer objects to have
		access to MAC address information
		"""
		self.receive_queue.put(datalink)

	def routeEthernetToMorse(self):
		"""
		Forwards ethernet transmissions to MorrowNet
		"""
		sock = self.socket
		while True:
			try:
				bytearray_ipheader_udpheader_msg, other_router_address = sock.recvfrom(1024)
				source_IP, source_port = other_router_address
				
				ipheader_udpheader_msg = bytearray_ipheader_udpheader_msg.decode('utf-8')
				IP = IPLayer(ipheader_udpheader_msg)

				dest_mac, source_mac= self.registry[IP.getHeader(0)], self.mac
				self.send_queue.put(DatalinkLayer(IP,(dest_mac,source_mac)))

				if self.verbose:
					print("Message received on Ethernet. Routed to MorrowNet.")
					print(" Src Router: {}".format(source_IP))
					print(" Dest MAC: {}".format(dest_mac))
					print(" Src MAC: {}".format(source_mac))
					print(" Dest IP: {}".format(IP.getHeader(0)))
					print(" Src IP: {}".format(IP.getHeader(1)))
					print(" Dest Port: {}".format(IP.getPayload().getHeader(0)))
					print(" Src Port: {}".format(IP.getPayload().getHeader(1)))
					print(" Message: {}".format(IP.getPayload().getPayload()))
					print(" ")
		

			except s.timeout:
				continue

	def routeMorseToEthernet(self):
		"""
		Forwards MorrowNet transmission to Ethernet
		and routes MorrowNet transmissions
		and assigns IP addresses on MorrowNet
		"""
		sock = self.socket
		while True:

			datalink = self.receive_queue.get(True)
			dest_mac, source_mac = datalink.getHeader(0), datalink.getHeader(1)
			dest_ip, source_ip  = datalink.payload.getHeader(0), datalink.payload.getHeader(1)
			dest_group, source_group = dest_ip[0], source_ip[0]

			if self.mac == dest_mac and self.group == dest_group:
				datalink.setHeader((self.registry[dest_ip],source_mac))
				self.send_queue.put(datalink)
				if self.verbose:
					print("Message received on MorrowNet. Routed to MorrowNet.")
					print(" Dest MAC: {}".format(datalink.getHeader(0)))
					print(" Src MAC: {}".format(datalink.getHeader(1)))
					print(" Dest IP: {}".format(datalink.getPayload().getHeader(0)))
					print(" Src IP: {}".format(datalink.getPayload().getHeader(1)))
					print(" Dest Port: {}".format(datalink.getPayload().getPayload().getHeader(1)))
					print(" Src Port: {}".format(datalink.getPayload().getPayload().getHeader(1)))
					print(" Message: {}".format(datalink.getPayload().getPayload().getPayload()))
					print(" ")
			elif self.mac == dest_mac and self.group != dest_group:
				if dest_ip == '00' and source_ip == '00':
					new_ip = ""
					while True:
						new_ip = self.group + chr(random.randint(65,90))
						if new_ip not in self.registry:
							break
					self.registry[new_ip] = source_mac
					datalink.setHeader((source_mac,self.mac))
					datalink.payload.setHeader((new_ip,'00'))
					self.send_queue.put(datalink)
					if self.verbose:
						print("Assigning IP on MorrowNet.")
						print(" Recipient MAC: {}".format(datalink.getHeader(0)))
						print(" Assigned IP: {}".format(datalink.getPayload().getHeader(0)))
						print(" ")
				else:
					bytearray_ipheader_udpheader_msg = bytearray(str(datalink.payload), encoding='UTF-8')
					dst_group_router = self.router_eth_ip[dest_group]
					sock.sendto(bytearray_ipheader_udpheader_msg, dst_group_router)
					if self.verbose:
						print("Message received on MorrowNet. Routed to Ethernet.")
						print(" Dest Router: {}".format(dst_group_router))
						print(" Dest IP: {}".format(datalink.getPayload().getHeader(0)))
						print(" Src IP: {}".format(datalink.getPayload().getHeader(1)))
						print(" Dest Port: {}".format(datalink.getPayload().getPayload().getHeader(1)))
						print(" Src Port: {}".format(datalink.getPayload().getPayload().getHeader(1)))
						print(" Message: {}".format(datalink.getPayload().getPayload().getPayload()))
						print(" ")


	
		
if __name__ == "__main__":
	router = Router()
