"""
netMessage.py
-------------
Author: Nick Francisci
Status: Incomplete & Untested
Description:
A class providing methods and storage for a string to be recieved or transmitted.
It can be initilized as either a message string with the relevant parameters (top-down)
or as a binary list (bottom-up).
Many instances of this are owned by the netTransportLayer

"""

class netMessage:

	def __init__(self, msg = None, mac = None, address = None, binary = []):

		# Setup from binary array (bottom-up)
		if msg is None and mac is None and address is None:
			self.binary = binary;

		# Setup from message (top-down)
		elif msg is not None and mac is not None and address is not None:
			self.setMsg(msg);
			self.setMACs(mac);
			self.setAddresses(address);

		# Report incorrect setup
		else:
			print ("ERROR: A netMessage object must be initilized with a Message, MAC, and address.")

	# Public Functions
	def getMACs(self):

	def getIPs(self):

	def getPorts(self):

	def getDestPort(self):

	def send(self):

	def add(self):

	# Private Functions
	def morseToIPV4(self):
	def IPV4ToMorse(self):
	
	def setMsg(self, msg):
	def setMACs(self, MACs):
	def setAddresses(self, Address):

	def wrapMachine(self, msg):
		"""
		Arguments:
			- msg: the message in binary format after the ECC has been added

		Returns:
			- The message in binary format with the header (ready for transmission)

		"""

	def unwrapMachine(self):

	def wrapECC(self, msg):
		"""
		Arguments:
			- msg: the message in binary format

		Returns:
			- The message in binary format with the ECC wrapper
		"""


	def unwrapECC(self):

	def wrapMAC(self):
	def unwrapMAC(self):

	def wrapIP(self):
	def unwrapIP(self):

	def wrapTransport(self):
	def unwrapTransport(self):
