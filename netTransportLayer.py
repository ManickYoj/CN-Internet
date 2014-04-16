"""
netTransportLayer.py
---------------
Author: Nick Francisci
Status: Incomplete & Untested
Description:
A wrapper for the morse transport protocol.
Provides functions specific to this traport protocol.
A single instance of this class should be owned by the netOS.

"""

class netTransportLayer(object):
	# System Functions
	def __init__(self):

	# Public Functions
	def sendto(self, msg, address):
		""" Setup a new netMessage() """

	def recvfrom(self,msg,address):
		""" Retrieve a netMessage() from the queue and return it """
