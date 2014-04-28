"""
morrowos.py
-----------
Author: Nick Francisci
Status: Incomplete & Untested
Description:
The overarching program controller.
New apps are instantiated from here and this class
controls and distributes resources. It owns the singleton
NIC class and is itself a singleton.

Operation:
	- On boot: starts a NIC layer and runs a thread that:
		- When the queue from 
	- Allows the user to boot apps. On app boot:
		- Creates a socket keyed to the app_id
"""

import morrownic


class MorrowOS(object):

	def __init__(self):
		self.nic = MorrowNIC()
		self.app_dict = dict()

	def createApp(self):
		app_id = 69
		return app_id

	def destroyApp(self, app_id):