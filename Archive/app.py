import threading as t

# App imports
import chatserver as cs
import chatclient as cc


class AppList(object):

    def __init__(self):
        self.apps = {'chatserver': cs.ChatServer, 'chatclient': cc.ChatClient}

    def runApp(self, app_type, app_id, send_queue):
        if app_type in self.apps:
            app = self.apps[app_type]
            t.Thread(target=app.__init__, args=[app_id, send_queue])
            t.setDaemon(True)
            t.start()
            return t
        else:
            return None

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
