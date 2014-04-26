class BaseLayer(object):

    def __init__(self, payload=None, verbose=False):
        self.payload = None
        self.verbose = verbose

        if isinstance(payload, BaseLayer) or payload is None:
            self.payload = payload

    def getNext(self):
        return self.payload


class DatalinkLayer(BaseLayer):

    def __init__(self, mac, payload=None, verbose=False):
        super(DatalinkLayer, self).__init__(payload, verbose)
        self.src_mac = mac[0]
        self.dest_mac = mac[1]

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
