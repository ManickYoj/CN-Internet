"""
portmanager.py
--------------
Author: Nick Francisci
Status: Complete & Untested
Description:
An interface between the sockets and the OS layer
that gives socket instances the ability to modify
their ports with (theoretically) protected methods
that do not grant OS access.

"""


class PortManager(object):

    def __init__(self, sock_dict, send_queue, ip):
        self.MIN_PORT = 65
        self.MAX_PORT = 90

        self.sock_dict = sock_dict
        self.send_queue = send_queue
        self.ip = ip

    # ----- Socket API ----- #
    def register(self, sock_queue):
        """
        Registers a socket with the OS and returns to it
        the IP of the Pi, the unique port generated for it,
        and the queue for submitting messages for transmission
        """
        port = self.findPort()
        self.sock_dict[port] = sock_queue
        return self.ip, port, self.send_queue

    def reassignPort(self, old_port, new_port):
        """
        Reassigns the port of the socket registered to the
        old_port to the port new_port if possible.
        """
        if old_port in self.sock_dict:
            if self.portValid(new_port):
                send_queue = self.sock_dict[old_port]
                del self.sock_dict[old_port]
                self.sock_dict[new_port] = send_queue
                return True
        return False

    def clearPort(self, port):
        """ Removes a socket from its port. """
        if port in self.sock_dict:
            del self.sock_dict[port]

    # ----- OS API ----- #
    def updateIP(self, ip):
        self.ip = ip

    # ------ Private Methods ----- #
    def findPort(self):
        """
        Finds an unused port and returns its index.
        Returns None if no ports are available.
        """
        for port in range(self.MIN_PORT, self.MAX_PORT+1):
            if self.portValid(port):
                return port

    def portValid(self, port):
        """ Checks if a given port may be assigned. """
        if port:
            if self.MIN_PORT <= port <= self.MAX_PORT:
                if not port in self.sock_dict:
                    return True
        return False
