"""
netSocket.py
-------------
Author: Nick Francisci
Status: Incomplete & Untested
Description:
A socket keyed to an app.
A single instance of this is owned by the app.

"""

class netSocket(object):
	# System Functions
	def __init__(self):
	def __enter__(self):
	def __exit__(self):

	# Public Functions
	def bind(self, address):
	def settimeout(self, timeout):
	def sendto(self, msg, address):
	def recvfrom(self, buflen):