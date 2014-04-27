"""
morrowstack.py
--------------
Author: Nick Francisci
Status: Incomplete & Untested
Description:
Contains the classes describing all stack layers.

Example Interfacing:
    - If constructed from the hardware (msg recieved):
        1. In NIC layer: Initilize Datalink(payload_string)
            a. Returns True if initilization goes through without errors
            b. Returns False if any initilizations fail

    - If constructed from the app (msg constructed):
        1. In sockets layer: Initilize Transport(message, (src_port, dest_port))
        2. In sockets layer: Initilize IP(Transport, (src_ip, dest_ip))
        3. In NIC layer: Initilize Datalink(IP, (src_mac, dest_mac))
        4. In NIC layer: Send Datalink.toBinary()
"""


class BaseLayer(object):
    """
    The base for all stack layer classes.
    Contains the initilization, getter, and setter methods for the
    header and payload of every layer.

    """

    def __init__(self, payload=None, header=None, verbose=False):
        self.setPayload(payload)
        self.setHeader(header)
        self.verbose = verbose

    # ----- Public Methods ----- #
    def getPayload(self):
        """ Getter method for payload. """
        return self.payload

    def setPayload(self, payload):
        """ Setter method with error-checking for payload. """
        self.checkPayload(payload)
        self.payload = payload

    def getHeader(self):
        """ Getter method for header. """
        return self.header

    def setHeader(self, header):
        """ Setter method with error-checking for header. """
        self.checkHeader(header)
        self.header = header

    # ----- Private Methods ----- #
    def checkPayload(self, payload):
        """ Checks to ensure that the payload meets format specifications. """
        if not (isinstance(payload, BaseLayer) or isinstance(payload, basestring)):
            raise ValueError("Error in the format of the payload of {}.").format(__name__)

    def checkHeader(self, header):
        """ Checks to ensure that the header meets format specifications. """
        if not (isinstance(header[0], basestring) and isinstance(header[1], basestring)):
            raise ValueError("Error in the format of the header of {}.").format(__name__)


class DatalinkLayer(BaseLayer):

    def __init__(self, payload=None, header=None, verbose=False):
        # Top down (Msg Constructed) initilization is handled by super call alone
        # Bottom up (Msg Recieved) initilization happens here
        if isinstance(payload, basestring):
            header = (payload[0], payload[1])
            payload = IPLayer(payload[2:], verbose=verbose)

        super(DatalinkLayer, self).__init__(payload, header, verbose)

        if self.verbose:
            print("DatalinkLayer initilized with a source MAC '{}'," +
                  " a dest MAC '{}', and a payload '{}'").format(self.header[0],
                                                                 self.header[1],
                                                                 self.payload)


class IPLayer(BaseLayer):

    def __init__(self, payload=None, header=None, transport_protocol=None, verbose=False):
        # Top down (msg constructed) initilization
        if isinstance(payload, TransportLayer):
            self.transport_protocol = transport_protocol

        # Bottom up (msg recieved) initilization
        elif isinstance(payload, basestring):
            header = (payload[:2], payload[2:4])
            self.transport_protocol = payload[4]
            if self.transport_protocol == 'E':
                payload = UDPLayer(payload[5:], verbose=verbose)

        super(IPLayer, self).__init__(payload, header, verbose)

        if self.verbose:
            print("IPLayer initilized with a source IP '{}'," +
                  " a dest IP '{}', a protocol '{}'," +
                  "and a payload '{}'").format(self.header[0],
                                               self.header[1],
                                               self.transport_protocol,
                                               self.payload)


class TransportLayer(BaseLayer):
    """ Stand in for base class of UDPLayer and (theoretically) TCPLayer. """
    def __init__(self, payload=None, header=None, verbose=False):
        super(TransportLayer, self).__init__(payload, header, verbose)


class UDPLayer(TransportLayer):
    def __init__(self, payload=None, header=None, verbose=False):
        # Top down (msg constructed) initilization
        if payload and header:
            self.length = len(payload)

        # Bottom up (msg recieved) initilization
        elif payload:
            header = (payload[0], payload[1])
            self.length = int(payload[2:4])
            payload = payload[4:]

        super(UDPLayer, self).__init__(payload, header, verbose)

        if self.verbose:
            print("UDPLayer initilized with a source port '{}'," +
                  " a dest port '{}', a length '{}'," +
                  "and a message '{}'").format(self.header[0],
                                               self.header[1],
                                               self.length,
                                               self.payload)

    def getLength(self):
        return self.length

if __name__ == "__main__":
    print("Running unit tests for {}").format(__file__)
    dl = DatalinkLayer("INIIINEEE06TESTMSG", verbose=True)
