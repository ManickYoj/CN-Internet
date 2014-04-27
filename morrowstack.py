# Example Intefacing:
#   - If constructed from the bottom up:
#       1. Initilize datalink(payload)
#           a. Returns True if initilization goes through without errors
#           b. Returns False if any initilizations fail
#
#   - If constructed from the top down:
#       1. Initilize Transport(message)
#       2. Initilize IP(Transport)
#       3. Initilize Datalink(IP)
#       4. Send Datalink.toBinary()


class BaseLayer(object):

    def __init__(self, payload=None, verbose=False):
        self.payload = None
        self.verbose = verbose

        if isinstance(payload, BaseLayer) or payload is None:
            self.payload = payload

        else:
            return False

        return True

    def getNext(self):
        return self.payload


class DatalinkLayer(BaseLayer):

    def __init__(self, mac, payload=None, verbose=False):
        super(DatalinkLayer, self).__init__(payload, verbose)
        self.src_mac = mac[0]
        self.dest_mac = mac[1]

        if payload:
            self.payload = IPLayer(payload[2:])

        if self.verbose:
            print("DatalinkLayer initilized with a source MAC '{}'," +
                  " a dest MAC '{}', and a payload '{}'").format(self.src_mac,
                                                                 self.dest_mac,
                                                                 self.payload)


class IPLayer(BaseLayer):

    def __init__(self, ip_data, payload, verbose=False):
        super(IPLayer, self).__init__(payload, verbose)
        self.src_ip = ip_data[0]
        self.dest_ip = ip_data[1]
        self.transport_protocol = ip_data[2]


if __name__ == "__main__":
    print("Running unit tests for {}").format(__file__)
    dl = DatalinkLayer("IN", verbose=True)
