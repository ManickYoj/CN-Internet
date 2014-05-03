import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from queue import Queue
from morrowutilities import charToBinaryDict,binaryToCharDict
import threading
from morrowstack import DatalinkLayer
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
	router_eth_ip = {"I":"192.168.100.73",
		     "E":"192.168.100.50",
		     "T":"192.168.100.84",
		     "R":"192.168.100.82"
		    }
	socket, AF_INET, SOCK_DGRAM, timeout = s.socket, s.AF_INET, s.SOCK_DGRAM, s.timeout

	def __init__(self):

		self.group = mac.my_group
		self.Router_Address = ("10.26.8.23",5073)

		receive_queue = Queue()

		self.socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
		self.socket.bind(self.Router_Address)
		self.socket.settimeout(2.0)

		super(Router,self).__init__(receive_queue)
		self.ip = '00'
		self.mac = 'R'
		self.registry = {}
		self.E2M = threading.Thread(target=self.routeEthernetToMorse)
		self.M2E = threading.Thread(target=self.routeMorseToEthernet)
		self.E2M.start()
		self.M2E.start()

	def forward(self,datalink):
		self.receive_queue.put(datalink)

	def routeEthernetToMorse(self):

		sock = self.socket
		while True:
			try:
				print(".")

				bytearray_ipheader_udpheader_msg, other_router_address = sock.recvfrom(1024)
				source_IP, source_port = other_router_address
				    
				ipheader_udpheader_msg = bytearray_ipheader_udpheader_msg.decode('utf-8')
				    
				    # --- relies on IP/UDP Protocal written by Hill et al --- #
				ipheader = ipheader_udpheader_msg[:7] # eg.'EA' + 'IB' + 'E' + 'EA'
				    #udpheader = ipheader_udpheader_msg[7:9] # eg. 'B' + 'C'
				    #msg = ipheader_udpheader_msg[9:]
				dst_ip, src_ip = ipheader[:2], ipheader[2:4] # ipheader example: 'EA' + 'IB' + 'E' + 'EA' where 'EA' is ip_to, 'IB' is ip_from
				    #dst_port, src_port = udpheader # udpheader example: 'BC' where B udp_to, C udp_from
						   
				print("Message routing from Ethernet to Morse:")
				print(ipheader_udpheader_msg)
				dest_mac = self.registry[dst_ip]
				source_mac = self.mac
				self.send_queue.put(DatalinkLayer(ipheader_udpheader_msg,(dest_mac,source_mac)))
		

			except s.timeout:
				continue

	def routeMorseToEthernet(self):
	
		sock = self.socket
		while True:
			try:
				print("*")
				datalink = self.receive_queue.get(True)
				if not datalink: raise timeout
				dest_mac = datalink.getHeader(0)
				source_mac = datalink.getHeader(1)
				dest_ip = datalink.payload.getHeader(0)
				source_ip = datalink.payload.getHeader(1)
				dest_group = dest_ip[0]
				source_group = source_ip[0]

				if self.mac == dest_mac and self.group == dest_group:
					datalink.setHeader((self.registry[dest_ip],source_mac))
					self.send_queue.put(datalink)
				elif self.mac == dest_mac and self.group != dest_group:
					if dest_ip == '00' and source_ip == '00' and source_mac not in self.registry.values():
						new_ip = ""
						while new_ip in self.registry:
							new_ip = self.group + chr(random.randint(65,90))
						rself.registry[new_ip] = source_mac
						datalink.setHeader((source_mac,self.mac))
						datalink.payload.setHeader((new_ip,'00'))
						self.send_queue.put(datalink)
					else:
						bytearray_ipheader_udpheader_msg = bytearray(str(datalink.payload), encoding='UTF-8')
						dst_group_router = self.router_eth_ip[destination_group]
						sock.sendto(bytearray_ipheader_udpheader_msg, dst_group_router)

			except timeout:
			    # standby_display(".") # print standby dots on the same line
			    continue

	
		
if __name__ == "__main__":
	router = Router()
