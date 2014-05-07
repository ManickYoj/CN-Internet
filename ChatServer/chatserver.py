import queue as q
import threading as t
from collections import OrderedDict
import user as u


class ChatServer(object):

    def __init__(self, ip=None, port=69, socktype=1):
        if socktype == 0:
            import socket as s
        else:
            import morrowsocket as s

        # Initilize variables
        self.serverlog = []
        self.users = {}
        self.buflen = 65500
        self.ip = ip
        self.port = port
        self.socket = None

        # Thread control booleans
        self.exit = False
        self.disp_output = True
        self.output_msgs = []

        # Server UI Setup
        self.available_cmds = OrderedDict([('help', self.help),
                                           ('show_log', self.showLog),
                                           ('clear_log', self.clearLog),
                                           ('exit', self.exit)])

        ## Client UI Setup
        #self.user_cmds = OrderedDict([('\\login')])

        # Start actual recieving thread
        server_thread = t.Thread(target=self.runServer)
        server_thread.setDaemon(True)
        server_thread.start()

        # Allow user interrupts to issue commands
        self.runCLI()

    # ----- Private UI Methods ----- #
    def runCLI(self):
        while not self.exit:
            input("\n")  # Continue to cmd prompt when user hits the enter key
            self.disp_output = False  # Temporarily stop displaying server output
            print("\n")

            cmd = input('--> Enter Cmd: ')
            cmd = cmd.split()

            if len(cmd) > 0 and cmd[0] in self.available_cmds:
                if len(cmd) >= 1:
                    args = cmd[1:]
                else:
                    args = []

                self.available_cmds[cmd[0]].__call__(args)

            # Resume server output and displayed the held messages
            self.disp_output = True
            for item in self.output_msgs:
                print(item)
            self.output_msgs = []

    def showLog(self, *args):
        print("#----- Start of Server Log ----- #")
        if self.serverlog:
            for (counter, item) in enumerate(self.serverlog):
                print("Entry No. {}:  ".format(counter) + item)
        print("#----- End of Server Log-----#")

    def clearLog(self, *args):
        self.serverlog = []
        print("#----- Server Log Cleared -----#")

    def help(self, *args):
        """ Display a list of commands and available applications. """

        if self.available_cmds:
            dir_text = "Enter commands in the format 'cmd [args]'. Available commands: \n"
            for cmd in self.available_cmds.keys():
                dir_text += " -" + cmd + "\n"
        else:
            dir_text = "No commands available."

        print(dir_text + "\n")

    def exit(self, *args):
        self.disp_output = False  # Catch any final messages and suppress them
        self.exit = True
        print("#----- Server Shutdown -----#")

    # ----- Private Message Methods ----- #
    def runServer(self):
        socket, AF_INET, SOCK_DGRAM, timeout = s.Socket, s.AF_INET, s.SOCK_DGRAM, s.timeout

        with socket(AF_INET, SOCK_DGRAM) as sock:

            # Socket setup
            self.socket = sock
            sock.bind((self.ip, self.port))
            sock.settimeout(1)

            print("Chat Server started on IP Address {} and port {}".format(self.ip, self.port))
            print("To enter a comand, first press the enter key, then enter the command at the displayed prompt.")

            # Main loop
            while not self.exit:
                try:
                    # Check socket & parse data
                    data = sock.recvfrom(self.buflen)
                    bytearray_msg, address = data
                    msg = bytearray_msg.decode("UTF-8")

                    # Message display & logging
                    msg_output = "\nMessage received from ip address {}, port {}:\n".format(address[0], address[1])
                    msg_output += msg + "\n"
                    self.serverlog.append(msg_output)

                    # Account for when input is being taken
                    if self.disp_output:
                        print(msg_output)
                    else:
                        self.new_msgs.append(msg_output)

                    # Add new users and relay messages
                    if address not in self.users:
                        self.login(msg, address)
                    else:
                        self.relayMessage(msg, address)

                # Allows socket's recvfrom to timeout safely
                except q.Empty:
                    continue

    def sendMessage(self, msg, address):
        """ Sends a message to the destination IP """
        if isinstance(msg, list):
            msg = ''.join(msg)

        # Send Message
        self.socket.sendto(msg.encode("UTF-8"), address)

    def relayMessage(self, msg, address):
        """ Repeates a message from the given source IP, if valid. """
        if len(msg) >= self.buflen:
            self.sendMessage("Message was too long and has not been sent.", address)
        else:
            for user in self.users:
                self.sendMessage(msg, user.address)

    # ----- User Commands ----- #
    def login(self, msg, address):
        if msg == "\\login":
            msg = msg.split()
            if len(msg) > 1:
                self.users[address] = msg[1]
                welcome = msg[1] + " has joined the server."
                print(welcome)
                self.serverlog.append(welcome)
                self.relayMessage(welcome)
            else:
                self.sendMessage("Login failed. No alias submitted.", address)

if __name__ == "__main__":
    ChatServer()
