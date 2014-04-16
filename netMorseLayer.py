"""
netMorseLayer.py
---------------
Author: Nick Francisci
Status: Partially Complete (Theoretically Functional), Untested
Description: 
A transport protocol that transmits and recieves in morse code.
Capable of acting as a router if initilized with routerMode as true.

TODO: Make routerMode functional for non-local transmission (ethernet to other LANs)
"""

import netLocalHardware as nlh
#import netEthernetHardware as neh
import netMessage as nm
import netAddressBookSetup as nABS
import collections as c
import pickle as p

class netMorseLayer:

	# ----- System Methods ----- #
	def __init__(self, my_mac, apps = [], router = 'T', routerMode = False):
		# Create a dictionary of queues keyed to each app's ID
		self.appQueues = {apps[i] : c.deque() for i in apps};

		# Initilize other class variables
		self.routerMode = routerMode;
		self.macDict = dict();
		self.mac = my_mac;
		self.local = nlh.netLocalHardware();

		if not routerMode:
			self.mac_dict['router'] = router;
		else:
			nABS.createAddressBook();
			self.mac_dict = self.addressBook();
			#self.ethernet = neh.netEthernetHardware();


	# ----- Public Methods ----- #
	def sendto(self, msg_text, address): 
		"""
		Setup a new netMessage and push it to the hardware for transmission.

		Arguments:
			- msg_text: the text of the message to send.
			- address: an (IP, Port) tuple (IPV4 format) of the address to send to
		"""

		# Create an appropriate MAC header
		dest_mac = self.macLookup(address);
		orig_mac = self.mac;
		mac = (dest_mac, orig_mac);

		# Create a netMessage object and send it
		msg = nm.netMessage(msg_text, mac, address);
		self.hardware.send(msg);


	def addApp(self, app_id):
		"""
		Creates a new queue for an app.

		Arguments:
			- app_id: the id of the app for whom to create a queue.
		"""
		self.appQueues[app_id] = c.deque();


	def removeApp(self, app_id):
		"""
		Removes an app's queue.

		Arguments:
			- app_id: the id of the app whose queue is to be deleted.
		"""

		del self.appQueues[app_id];


	def addMessage(self, msg):
		"""
		Push a new message to the appropriate app's queue or routes it appropriately

		Arguments:
			- msg: a netMessage object
		"""
		# Do nothing if the message is not addressed to this computer.
		if not msg.getDestMAC() == self.mac: return;

		if self.routerMode: route(msg);
		else: self.appQueues[msg.getDestPort()].appendLeft(msg);


	def recvfrom(self, app_id):
		"""
		Retrieve a netMessage from the appropriate queue and returns it.

		Arguments:
			- app_id: the ide of the app whose queue is to be checked.

		Returns: a stored (message, address(in IPV4 format)) tuple if a message exists and None otherwise.

		"""

		if self.appQueues[app_id]:
			msg = self.appQueues.pop();
			return (msg.getMsg(), msg.getAddress());
		else return None;


	# ----- Private Methods ----- #
	def route(self, msg):
		"""
		Reroutes a message to the appropriate MAC.

		Arguments:
			- msg: the netMessage to reroute.
		"""

		msg.setDestMAC(self.macLookup(msg.getDestIP()));
		self.hardware.send(msg);


	def macLookup(self, ip):
		"""
		Looks up a mac address in the mac_dict and returns it.

		Arguments:
			- ip: the ip (morse formatted string) to look up.

		Returns: the MAC corresponding to the desired ip.

		"""

		if ip in self.macDict: return self.macDict[ip];
		else: 
			if not self.routerMode:	return self.macDict['router'];
			else: print("ERROR: MAC not in address book!")


	def addressBook(self):
		"""
		Loads a file of local addresses for the router to use.

		Returns: a dictionary of local MAC address to IP relations.
		"""

		with open('addressBook.pkl', 'rb') as f:
			ab = pickle.load(f);

		return ab;