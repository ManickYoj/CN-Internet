"""
morrowstack.py
--------------
Author: Nick Francisci
Status: Basic Functionality Complete & Tested
Description:
Contains the classes describing all stack layers.

Example Interfacing:
    - If constructed from the hardware (msg recieved):
        1. In NIC layer: Initilize Datalink(payload_string)
            a. Raises ValueError at appropriate stack level if any initilizations fail

    - If constructed from the app (msg constructed):
        1. In sockets layer: Initilize TransportLayer(message, (src_port, dest_port))
        2. In sockets layer: Initilize IPLayer(Transport, (src_ip, dest_ip), transport_protocol)
        3. In NIC layer: Initilize DatalinkLayer(IP, (src_mac, dest_mac))
        4. In NIC layer: Send Datalink.toBinary()


TODO: Ensure that length/port parameters are parsed to int format correctly
TODO: Create toBinary method if it is to be used
TODO: Make more robust testing for proper lengths/formats of attributes beyond type
"""


class BaseLayer(object):
    """
    The base for all stack layer classes.
    Contains a basic initilization, getter, and setter methods for the
    header and payload of every layer.

    """

    def __init__(self, payload=None, header=None, verbose=False):
        self.verbose = verbose
        self.setPayload(payload, True)
        self.setHeader(header, True)

    # ----- Public Methods ----- #
    def getPayload(self):
        """ Getter method for payload. """
        return self.payload

    def setPayload(self, payload, init=False):
        """ Setter method with error-checking for payload. """
        self.checkPayload(payload)
        self.payload = payload

    def getHeader(self):
        """ Getter method for header. """
        return self.header

    def setHeader(self, header, init=False):
        """ Setter method with error-checking for header. """
        self.checkHeader(header)
        self.header = header

    # ----- Private Methods ----- #
    def checkPayload(self, payload):
        """ Checks to ensure that the payload meets format specifications. """
        if not (isinstance(payload, BaseLayer)):
            exception_text = "Error in the format of the payload of {}.".format(self)
            raise ValueError(exception_text)

    def checkHeader(self, header):
        """ Checks to ensure that the header meets format specifications. """
        if not (isinstance(header[0], str) and isinstance(header[1], str)):
            exception_text = "Error in the format of the header of {}.".format(self)
            raise ValueError(exception_text)


class DatalinkLayer(BaseLayer):
    """ Morse implementation of the MAC/Datalink layer. """
    def __init__(self, payload=None, header=None, verbose=False):
        # Top down (Msg Constructed) initilization is handled by super call alone
        # Bottom up (Msg Recieved) initilization happens here
        if isinstance(payload, str):
            header = (payload[0], payload[1])
            payload = IPLayer(payload[2:], verbose=verbose)

        super(DatalinkLayer, self).__init__(payload, header, verbose)

        if self.verbose:
            print("DatalinkLayer initilized with a source MAC '{}', a dest MAC '{}', and a payload '{}'".format(self.header[0],
                                                                                                                self.header[1],
                                                                                                                self.payload))


class IPLayer(BaseLayer):
    """ Morse implementation of the IP layer. """
    def __init__(self, payload=None, header=None, transport_protocol=None, verbose=False):
        # Top down (msg constructed) initilization
        if isinstance(payload, TransportLayer) and header and transport_protocol:
            self.transport_protocol = transport_protocol
        elif isinstance(payload, TransportLayer) and not (header and transport_protocol):
            raise ValueError("Error in attemping to initilize IPLayer from app data: invalid " +
                             "value entered for either header or transport_protocol")

        # Bottom up (msg recieved) initilization
        elif isinstance(payload, str):
            header = (payload[:2], payload[2:4])
            self.setTransportProtocol(payload[4])
            if self.transport_protocol == 'E':
                payload = UDPLayer(payload[5:], verbose=verbose)

        super(IPLayer, self).__init__(payload, header, verbose)

        if self.verbose:
            print("IPLayer initilized with a source IP '{}', a dest IP '{}', a protocol '{}', and a payload '{}'".format(self.header[0],
                                                                                                                         self.header[1],
                                                                                                                         self.transport_protocol,
                                                                                                                         self.payload))

    # ----- Public Methods ----- #
    def getTransportProtocol(self):
        """ Getter method for transport_protocol attribute. """
        return self.transport_protocol

    def setTransportProtocol(self, transport_protocol):
        """ Setter method for transport_protocol with error-checking. """
        self.checkTransportProtocol(transport_protocol)
        self.transport_protocol = transport_protocol

    # ----- Private Methods ----- #
    def checkTransportProtocol(self, transport_protocol):
        """ Checks to ensure that the transport_protocol attribute matches format requirements. """
        if not(isinstance(transport_protocol, str) and len(transport_protocol)) == 1:
            raise ValueError("Invalid transport protocol value entered.")


class TransportLayer(BaseLayer):
    """ Stand in for base class of UDPLayer and (theoretically) TCPLayer. """
    def __init__(self, payload=None, header=None, verbose=False):
        super(TransportLayer, self).__init__(payload, header, verbose)


class UDPLayer(TransportLayer):
    """ Morse implementation of UDP Transport Layer. """
    def __init__(self, payload=None, header=None, verbose=False):
        # Top down (msg constructed) initilization
        if payload and header:
            self.length = len(payload)

        # Bottom up (msg recieved) initilization
        elif payload:
            header = (payload[0], payload[1])  # TODO: Base36 Parse this
            self.length = int(payload[2:4])  # TODO: ASCII Parse this, PS, this gets overwritten automatically
            payload = payload[4:]

        super(UDPLayer, self).__init__(payload, header, verbose)

        if self.verbose:
            print("UDPLayer initilized with a source port {!r}, a dest port {!r}, a length {!r}, and a message {!r}".format(self.header[0],
                                                                                                                            self.header[1],
                                                                                                                            self.length,
                                                                                                                            self.payload))

    # ----- Public Methods ----- #
    def getLength(self):
        """ Getter method for length attribute. """
        return self.length

    def setPayload(self, payload, init=False):
        """ Override for BaseLayer setPayload. Includes recalculation of  payload length. """
        self.checkPayload(payload)
        self.payload = payload
        if not init:  # Allows length attribute of recieved message to take the place of a calculated message length
            self.length = len(payload)

        if self.verbose and not init:  # This message is turned off for initilization
            print("Message set as {!r} and message length calculated as {!r}.".format(self.payload, self.length))

    # ----- Private Methods ------ #
    def checkPayload(self, payload):
        """ Override of BaseLayer checkPayload. Checks for payload type as string instead of BaseLayer. """
        if not(isinstance(payload, str)):
            raise ValueError("Message is not a string!")

# ----- Unit Testing ----- #
if __name__ == "__main__":
    print("Running unit tests for {!s}".format(__file__))

    print("Attempting bottom up (msg recieved) stack construction...")
    dl = DatalinkLayer("INIIINEEE06RECVMSG", verbose=True)
    print(" ")

    print("Attempting top down (msg constructed) stack construction...")
    udp = UDPLayer("APPMSG", ("E", "E"), verbose=True)
    ip = IPLayer(udp, ("IN", "II"), "E", verbose=True)
    dl = DatalinkLayer(ip, ("N", "I"), verbose=True)
