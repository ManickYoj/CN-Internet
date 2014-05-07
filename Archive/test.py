import threading as t
import time
from collections import OrderedDict

class Test(object):
	def __init__(self):
		self.verbose = True

		t.Thread(target=self.recvTest).start()
		self.sendTest()


	def recvTest(self):
		while True:
			if self.verbose:
				print(".")
			time.sleep(1)

	def sendTest(self):
		while True:
			first_cmd = raw_input("Hit 'Enter' at any point for input prompt.")
			self.verbose = False
			cmd = raw_input("Enter Input: ")
			print("Your command was " + cmd)
			self.verbose = True

def func(args):
	print(args)

available_cmds = OrderedDict([('help', 1),
                                 ('show_log', 2),
                                 ('clear_log', 3),
                                 ('exit', 4)])
func_list = {'func': func}

for item in available_cmds.keys():
	print(item)

func_list['func'].__call__('test')
