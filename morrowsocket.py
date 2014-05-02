"""
morrowsocket.py
---------------
Author: Nick Francisci
Status: Complete & Partially Tested
Description: 
The replacement for sockets in our stack, expected to be
used with any app that extends the App class. An app that
extends the app class will automatically have a properly
configured socket available to it simply as self.socket

TODO: 
- Less hardcoding/more portability for other AFs/protocols
- Mo' Docstrings

"""

import morrowstack as ms
import queue as q

AF_INET = 2
SOCK_DGRAM = 2
timeout = 2

class MorrowSocket(object):
	# ----- System Methods ----- #
	def __init__(self, family=2, protocol=2, port=69, send_queue=None, debug=False):
		self.debug = debug

		self.port = port
		self.ip = '0.0.48.48' # Corresponds to a Morse '00' 
							  # (which should automatically trigger an IP assignment request from the router)

		self.send_queue = send_queue
		self.recv_queue = q.Queue()
		self.timeout = None

		self.family = family
		self.protocol = protocol
		self.protocols = {protocol: 'E'} # Heh... 

	def __enter__(self):
		return self

	def __exit__(self, *T):
		return not any((T))

	# ----- Public Methods ----- #
	def bind(self, address):
		self.ip = address[0]
		#self.port = address[1] # Double Heh...

		if self.debug:
			print("Socket bound with IP {} and port {}").format(self.ip, self.port)

	def settimeout(self, timeout):
		self.timeout = timeout

	def sendto(self, msg, address):
		# Construct UDP Layer
		dest_port = self.IPV4ToMorse(address[1])
		src_port = self.IPV4ToMorse(self.port)
		udp = ms.UDPLayer(msg.decode("UTF-8"), (dest_port, src_port))

		# Construct IP Layer
		dest_ip = self.IPV4ToMorse(address[0])
		src_ip = self.IPV4ToMorse(self.ip)
		ip = ms.IPLayer(udp, (dest_ip, src_ip), protocols[self.protocol])

		# Send Packet
		send_queue.put(ip)

	def recvfrom(self, buflen=65536):
		try:
			ip = self.recv_queue.get(True, self.timeout)
			if ip.getLength() < buflen:
				address = (self.MorseToIPV4(ip.getHeader(1)), self.MorseToIPV4(ip.getPayload().getHeader(1)))
				msg = ip.getPayload().getPayload().encode("UTF-8")
				return msg, address
		except q.Empty:
			raise RuntimeException("No messages available.")

	def putmsg(self, msg):
		self.recv_queue.put(msg)

	# ----- Private Methods ----- #
	def IPV4ToMorse(self, ipv4):
		# Translate port by ASCII value (int->chr)
		if isinstance(ipv4, int):
			return chr(ipv4)
		# Translate IPV$ by ASCII value (int->chr)
		elif isinstance(ipv4, str):
			ipv4 = ipv4.split(".")
			return chr(int(ipv4[2])) + chr(int(ipv4[3]))
		else:
			raise ValueError("Unable to parse IPV4 string to morse!")

	def MorseToIPV4(self, morse):
		# Translate port by ASCII value (chr->int)
		if len(morse)==1:
			return ord(morse)
		# Translate IPV4 by ASCII value (chr->int)
		elif len(morse)==2:
			return "0.0.{}.{}".format(ord(morse[0]), ord(morse[1]))
		else:
			raise ValueError("Unable to parse morse string to IPV4!")

# ------ Unit Testing ----- #
msock = MorrowSocket(send_queue = q.Queue(), debug=True)

# Test Recv Functionality
udp = ms.UDPLayer("APPMSG", ("E", "E"))
ip = ms.IPLayer(udp, ("IN", "II"), "E")
msock.putmsg(ip)
msg, address = msock.recvfrom()
print(msg.decode("UTF-8"))
print(address)