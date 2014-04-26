"""
netMessage.py
-------------
Author: Nick Francisci
Status: Incomplete & Untested
Description:
A class providing methods and storage for a string to be recieved or
transmitted.
It can be initilized as either a message string with the relevant
parameters (top-down)
or as a binary list (bottom-up).
Many instances of this are owned by the netTransportLayer

"""

import netTranslate as nt


class netmessage:

    # ----- System Methods ----- #
    def __init__(self, msg_text=None, mac=None,
                 dest_ad=None, orig_ad=None, binary=None):

        # Setup from binary array with header and stop code stripped off (bottom-up)
        if(not msg_text and not mac and not dest_ad
           and not orig_ad and binary is not None):
            self.parsebinary(binary)

        # Setup from app-level message data (top-down)
        elif msg_text and mac and dest_ad and orig_ad:
            self.msg_text = msg_text
            self.dest_mac = mac[0]
            self.orig_mac = mac[1]
            self.dest_ip = dest_ad[0]  # IPV4 format
            self.orig_ip = orig_ad[0]  # IPV4 format
            self.orig_port = dest_ad[1]  # IPV4 format
            self.dest_port = orig_ad[1]  # IPV4 format

        # Report incorrect setup
        else:
            print("ERROR: A netMessage object must be initilized with" +
                  "a Message, MAC, and address.")

    # ----- Public Methods ----- #
    def getorigmac(self):
        return self.orig_mac

    def getdestmac(self):
        return self.dest_mac

    def getdestportasipv4(self):
        return self.dest_port

    def add(self, new_bits):
        self.binary.add(new_bits)

    # ----- Private Methods ----- #
    def parsebinary(self, binary):
        """ Converts a binary array with to useable data """
        binary = self.decodeecc(binary)

    def morsetoipv4(self, address):
        """ Converts a morse address to an IPV4 address. """
        ip_from_morse = address[0]
        port_from_morse = address[1]

        ip_from_str = "0.0.{}.{}".format(ord(ip_from_morse[0]),
                                         ord(ip_from_morse[1]))
        port_from = ord(port_from_morse)

        return ip_from_str, port_from

    def ipv4tomorse(self, address):
        """ Converts an IPV4 address to a morse address. """
        new_address = address[0].split(".")
        new_address.append(address[1])
        new_address = [int(letter_code) for letter_code in new_address]

        ip_addr = chr(new_address[2]) + chr(new_address[3])
        port = chr(new_address[4])

        return ip_addr, port

    def decodeecc(self, binary):
        """
        Arguments:
            - msg: the message in binary format

        Returns:
            - The message in binary format with the ECC wrapper
        """

        return binary


if __name__ == "__main__":
    print("Unit tests for {}").format(__file__)
    print(" ")

    print("Initilizing netmessage with no args...")
    nm = netmessage()
    print(" ")

    print("Initilizing netmessage with binary args...")
    nm = netmessage(binary=[])
    print("Testing netmessage with binary args...")
    nm.add([1, 1, 1, 1, 1])
    print("MAC DEST: {}\nMAC ORIG: {}").format(nm.dest_mac,
                                               nm.orig_mac)
    print(" ")

    print("Initilizing netmessage with message args...")
    nm = netmessage(msg_text="hello world", mac=("I", "N"),
                    dest_ad=("II", 69), orig_ad=("II", 69))
