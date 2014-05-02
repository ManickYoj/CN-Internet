#TODO OPCODES! YAY!

import MorrowSocket as ms

class App(object):
	def __init__(self, app_id, send_queue):
		self.socket = ms.MorrowSocket(port=app_id, send_queue=send_queue)

	def pushRecvdMsg(self, msg):
		self.socket.putmsg(msg)
