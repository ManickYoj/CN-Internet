"""
moros.py
-----------
Author: Nick Francisci
Status: Complete & Untested
Description:
The overarching program controller.
New apps are instantiated from here and this class
controls and distributes resources. It owns the singleton
NIC class and is itself a singleton.

"""

# Functionality Imports
import morrownic as mn
import morrowstack as ms
import portmanager as pm
import threading as t
import queue as q
import sys

# App Imports
sys.path.insert(0, 'ChatServer')
sys.path.insert(1, 'ChatClient')
import chatserver as cs
import chatclient as cc


class MorOS(object):

    def __init__(self, debug=False):
        # Initilize variables
        self.debug = debug
        self.sock_dict = {}

        self.available_cmds = {'exit': self.exit, 'help': self.help, 'run': self.run}
        self.available_apps = {'chatserver': cs.ChatServer, 'chatclient': cc.ChatClient}

        # Monitor incoming messages and direct them to appropriate sockets
        self.nic = mn.MorrowNIC(self.monitoredQueue(self.msgsToSock))

        # Setup a global socket registry system and relay submitted messages
        global port_manager
        port_manager = pm.PortManager(self.sock_dict, self.monitoredQueue(self.msgsFromSock), self.nic.getIP())

        # Run UI
        print("#----- MorOS booted. -----#")
        self.runCLI()

    # ------ Private UI Methods ----- #
    def runCLI(self):
        """
        Runs a command line interface that allows the user to start new apps by name.
        """
        self.available_cmds['help'].__call__()

        while True:
            cmd = input('--> Enter Cmd: ')
            print("\n")
            cmd = cmd.split()

            if len(cmd) > 0 and cmd[0] in self.available_cmds:
                if len(cmd) >= 1:
                    args = cmd[1:]
                else:
                    args = []

                self.available_cmds[cmd[0]].__call__(args)

    def help(self, *args):
        """ Display a list of commands and available applications. """

        if self.available_cmds:
            dir_text = "Enter commands in the format 'cmd [args]'. Available commands: \n"
            for cmd in self.available_cmds.keys():
                dir_text += " -" + cmd + "\n"
        else:
            dir_text = "No commands available."

        if self.available_apps:
            app_txt = "Available applications to run: "
            for app in self.available_apps.keys():
                app_txt += " -" + app + "\n"
        else:
            app_txt = "No applications available."

        print(dir_text + "\n" + app_txt + "\n")

    def exit(self, *args):
        sys.exit(0)

    def run(self, *args):
        if args:
            if args[0] in self.available_apps:
                self.available_apps[args[0]].__init__()
        else:
            print("Invalid app name.")

    # ----- Private Message Relay Methods ----- #
    def monitoredQueue(self, monitorFunc):
        """
        Initilizes a queue such that messages in that queue will be monitored
        and acted on by the passed in monitorFunc.
        """
        m_queue = q.Queue()
        m_thread = t.Thread(target=monitorFunc, args=[m_queue])
        m_thread.setDaemon(True)
        m_thread.start()
        return m_queue

    def msgsToSock(self, recv_queue):
        """
        Relays messages from the recv_queue to the appropriate
        socket if that socket exists.
        """
        while True:
            try:
                msg = recv_queue.get(True)
                if isinstance(msg, ms.IPLayer):
                    dest_port = msg.getPayload().getHeader(0)
                    if dest_port in self.sock_dict:
                        self.sock_dict[dest_port].put(msg)

            except q.Empty:
                continue

    def msgsFromSock(self, send_queue):
        """ Relays messages from the send_queue to the nic. """
        while True:
            try:
                msg = send_queue.get(True)
                if isinstance(msg, ms.IPLayer):
                    self.nic.send(msg)
            except q.Empty:
                continue

if __name__ == "__main__":
    moros = MorOS(debug=False)
