"""
netAddressBookSetup.py
----------------------
Author: Nick Francisci
Status: Complete & Tested
Description:
A helper script for the project.
This script pickles a dict of MAC Address to IP correspondences for future use by netMorseLayer.py.

"""

import pickle as p

def createAddressBook():
		# Create Dictionary
	ab = {
		# IP : MAC,
		"II" : "I",
		"IN" : "N",
		"ID" : "D",
		"IR" : "R"
		}

	# Pickle Dictionary
	with open('addressBook.pkl','wb') as f:
		p.dump(ab, f);


if __name__ == "__main__":
	createAddressBook();
