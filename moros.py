"""
moros.py
-----------
Author: Nick Francisci
Status: Incomplete & Untested
Description:
The overarching program controller.
New apps are instantiated from here and this class
controls and distributes resources. It owns the singleton
NIC class and is itself a singleton.

Operation:
    - On boot: starts a NIC layer and runs a thread that:
        - When the queue from 
    - Allows the user to boot apps. On app boot:
        - Creates a socket keyed to the app_id
"""

#import morrownic
import queue as q
import threading
import time
import sys
import os


class MorOS(object):
    def __init__(self, timeout=1, debug=False):
        self.debug = debug

        # Setup 
        self.apps = dict()  # A dictionary of all of the Apps owned by the OS, with port/app_id as the key
        self.timeout = timeout
        self.close = False

        # Setup NIC message monitoring
        recv_queue = self.createMonitoredRecvQueue()
        if not debug:
            import morrownic
            self.nic = MorrowNIC(recv_queue)

        # Run UI & Normal Operations
        self.runCLI()

        # Shutdown Gracefully
        self.__exit__()

    # ------ Private UI Methods ----- #

    def runCLI(self):
        """
        Runs a command line interface that allows the user to start new apps by name.
        """
        directions = ("Enter commands in the format 'cmd [args]'.\nSuggestions: 'run chatserver', 'run router', 'help', 'close'")
        print("#----- MorOS booted and awaiting commands. -----#")
        print(directions)
        while not self.close:
            cmd = input('Cmd: ')
            cmd = cmd.split()

            if len(cmd)<1:
                cmd = "ERROR"

            if cmd[0] == 'run' and len(cmd)>1:
                if cmd[1] == 'router':
                    self.startRouterMode()
                else:
                    self.createApp(cmd[1])
            elif cmd[0] == 'close':
                return
            elif cmd[0] == 'help':
                print(directions)
            else:
                print("Invalid command.")
                print(directions)

    # ------ Router Methods ------ #
    def startRouterMode(self):
        print("Route!")

    # ------ Private App Methods ----- #
    def createApp(self, app_type):
        """ 
        Initilizes a new App with a monitored send queue and unique app ID/port.
        """
        # Generate an app ID/port
        app_id = 69
        while app_id in self.apps:
            app_id += 1

        # Create a monitored sending queue for the app to use
        send_queue = self.createMonitoredSendQueue()

        try:
            new_app = App(app_id, send_queue, app_type)
            self.apps[app_id] = new_app
        except ValueError:
            send_queue.put(str(self))
            print("ERROR: No app with this name installed")

    def destroyApp(self, app_id):
        """ Gracefully exits the specified app and removes it from the OS's self.apps dict. """
        # Tells the thread monitoring the send_queue to end itself
        self.apps[app_id].send_queue.put(str(self))

        # Removes the app from the list of apps and allows garbage collection to delete
        # the instance of the app and its children
        del self.apps[app_id]

    # ----- Private Queue Creation Methods ----- #
    def createMonitoredRecvQueue(self):
        """ Creates and returns a monitored recieving queue. """
        recv_queue = q.Queue()
        threading.Thread(target=self.monitorRecv, args=[recv_queue])
        return recv_queue

    def monitorRecv(self, recv_queue):
        """
        A thread-method that monitors the NIC's recieving queue and passes on its messages
        to the appropriate App, if one exists. 
        """
        while not self.close:
            # Get message from the NIC and check its destination port
            msg = recv_queue.get(True, self.timeout)
            dest_port = msg.getPayload().getHeader(0)

            # If the message is addressed to an open app, pass on the message.
            # Otherwise, discard the message.
            if dest_port in self.apps:
                self.apps[dest_port].recv_queue.put(msg)

    def createMonitoredSendQueue(self):
        """ Creates and returns a monitored sending queue. """
        send_queue = q.Queue()
        threading.Thread(target=self.monitorSend, args=[send_queue])
        return send_queue

    def monitorSend(self, send_queue):
        """ A thread-method to send any messages in the passed send_queue. """
        while not self.close:
            msg = send_queue.get(True, self.timeout)

            if msg == str(self):
                return
            else:
                self.nic.send()

    def __enter__(self):
        return self

    def __exit__(self):
        # Apps will check this in <=self.timeout time and will shutdown
        self.close = True

        # Destroy remaining apps
        for app_id in self.apps.keys():
            self.destroyApp(app_id)

        # Wait for all threads to close and notify the user what percent have been closed
        orig_number = threading.active_count()-1
        while not threading.active_count() == 1:
            print("thread count: " + str(threading.active_count()))
            ratio = 1 - threading.active_count()/orig_number
            percent = ratio * 100
            print("Exiting: " + str(percent))
            time.sleep(.5)

        # Exit program
        sys.exit(0)

class App(object):
    def __init__(self, app_id, send_queue, app_type):
        if not app_type in ["chatserver"]:
            raise ValueError("ERROR: No app with this name installed")

        self.send_queue = send_queue
        self.recv_queue = q.Queue()

        self.initApp(app_type)

    def initApp(self, app_type):
        if app_type == 'chatserver':
            self.app = ExtChatServer()

# Import the chatserver module
sys.path.append('ChatServer')
from chatserver import ChatServer

class ExtChatServer(ChatServer):
    def __init__(self):
        print("ExtChatServer!")


class Socket(object):
    def __init__(self):
        print("Socket!")

if __name__ == "__main__":
    os = MorOS(debug=True)