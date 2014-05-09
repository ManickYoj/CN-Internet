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
import builtins

AF_INET = 2
SOCK_DGRAM = 2
timeout = 1


class Socket(object):

    # ----- System Methods ----- #
    def __init__(self, family=2, protocol=2, debug=False):
        self.debug = debug

        self.recv_queue = q.Queue()
        morse_ip, self.port, self.send_queue = port_manager.register(self.recv_queue)
        self.ip = self.MorseToIPV4(morse_ip)

        self.timeout = 1

        self.family = family
        self.protocol = protocol
        self.protocols = {protocol: 'E'}  # Heh...

        if self.debug:
            print("Socket started up with IP {} and port {}".format(self.ip, self.port))

    def __enter__(self):
        return self

    def __exit__(self, *T):
        port_manager.clearPort(self.port)
        return not any((T))

    # ----- Public Methods ----- #
    def bind(self, address):
        if self.debug:
            print("IP bind is not currently supported. IP will remain as {}.".format(self.ip))
        if port_manager.reassignPort(self.port, address[1]):
            self.port = address[1]

        if self.debug:
            print("Socket rebound to port {}".format(self.ip, self.port))

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
        ip = ms.IPLayer(udp, (dest_ip, src_ip), self.protocols[self.protocol])

        # Send Packet
        self.send_queue.put(ip)

    def recvfrom(self, buflen=65536):

        try:
            ip = self.recv_queue.get(True, self.timeout)

            if self.debug:
                    print("Message processed in the Socket:")
                    print(" Dest IP: {}".format(ip.getHeader(0)))
                    print(" Src IP: {}".format(ip.getHeader(1)))
                    print(" Dest Port: {}".format(ip.getPayload().getHeader(0)))
                    print(" Src Port: {}".format(ip.getPayload().getHeader(1)))
                    print(" Message: {}".format(ip.getPayload().getPayload()))
                    print(" ")

            # Check IP, Port, & Length
            if self.ip == self.MorseToIPV4(ip.getHeader(0)) and self.port == self.MorseToIPV4(ip.getPayload().getHeader(0)):
                if ip.getLength() < buflen:
                    address = (self.MorseToIPV4(ip.getHeader(1)), self.MorseToIPV4(ip.getPayload().getHeader(1)))
                    msg = ip.getPayload().getPayload().encode("UTF-8")
                    return msg, address
        except q.Empty:
            raise

    def putmsg(self, msg):
        self.recv_queue.put(msg)
        if self.debug:
            print("Added a message to the recieve queue.")

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
        if len(morse) == 1:
            return ord(morse)
        # Translate IPV4 by ASCII value (chr->int)
        elif len(morse) == 2:
            return "0.0.{}.{}".format(ord(morse[0]), ord(morse[1]))
        else:
            raise ValueError("Unable to parse morse string to IPV4!")

# ------ Unit Testing ----- #
if __name__ == "__main__":
    msock = MorrowSocket(debug=True)

    # Test Recv Functionality
    udp = ms.UDPLayer("APPMSG", ("E", "E"))
    ip = ms.IPLayer(udp, ("IN", "II"), "E")
    msock.putmsg(ip)
    msg, address = msock.recvfrom()
    print(msg.decode("UTF-8"))
    print(address)
