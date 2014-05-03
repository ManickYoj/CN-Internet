#TODO OPCODES! YAY!

import morrowsocket as ms
import socket as s


class App(object):

    def __init__(self, app_id=None, send_queue=None):
        self.sock_type = None

        if app_id and send_queue:
            self.socket = ms.MorrowSocket(port=app_id, send_queue=send_queue)
            self.sock_type = 'morse'
        else:
            self.socket = s.socket(2, 2)
            self.sock_type = 'std'

    def pushRecvdMsg(self, msg):
        if self.sock_type == 'morse':
            self.socket.putmsg(msg)
