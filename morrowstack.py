class BaseLayer(object):

    def __init__(self, payload=None, verbose=False):
        if isinstance(payload, BaseLayer) or payload is None:
            self.payload = payload
            self.verbose = verbose

            if self.verbose:
                print("BaseLayer initilized with payload {}.").format(payload)


class DatalinkLayer(BaseLayer):

    def __init__(self, payload=None, verbose=False):
        super(DatalinkLayer, self).__init__(payload, verbose)

if __name__ == "__main__":
    print("Running unit tests for {}").format(__file__)
    dl = DatalinkLayer(None, True)
