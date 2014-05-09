import queue as q
import threading as t
from collections import OrderedDict
import morrowsocket as s
import time

class ChatClient(object):

    def __init__(self, ip=None, port=69):

        # Initilize variables
        self.chatlog = []
        self.buflen = 65500
        self.ip = ip
        self.port = port
        self.dest_ip = self.ip
        self.dest_port = self.port
        self.socket = None

        # Thread control booleans
        self.closing = False
        self.disp_output = True
        self.output_msgs = []

        # UI Setup
        self.available_cmds = OrderedDict([('\\setDestIP', self.setDestIP),
                                           ('\\setDestPort', self.setDestPort),
                                           ('\\help', self.help),
                                           ('\\showLog', self.showLog),
                                           ('\\clearLog', self.clearLog),
                                           ('\\close', self.close)])

        # Start actual recieving thread
        recv_thread = t.Thread(target=self.runRecv)
        recv_thread.start()

        self.runCLI()

    # ----- Private UI Methods ----- #
    def runCLI(self):
        while not self.closing:
            input()  # Continue to cmd prompt when user hits the enter key
            self.disp_output = False  # Temporarily stop displaying server output
            print("\n")

            cmd = input('--> Enter Cmd or Msg: ')

            if len(cmd) > 0:
                cmd = cmd.split()
                if cmd[0] in self.available_cmds:
                    if len(cmd) >= 1:
                        args = cmd[1:]
                    else:
                        args = []

                    self.available_cmds[cmd[0]].__call__(args)
                else:
                    self.sendMessage(cmd)

            # Resume reciever output and displayed the held messages
            self.disp_output = True
            for item in self.output_msgs:
                print(item)
            self.output_msgs = []

    def setDestIP(self, *args):
        if not args:
            return
        elif not args[0]:
            return
        self.dest_ip = args[0][0]

    def setDestPort(self, *args):
        if not args:
            return
        elif not args[0]:
            return

        self.dest_port = int(args[0][0])

    def showLog(self, *args):
        print("#----- Start of Chat Log ----- #")
        if self.chatlog:
            for (counter, item) in enumerate(self.chatlog):
                print("Entry No. {}:  ".format(counter) + item)
        print("#----- End of Chat Log-----#")

    def clearLog(self, *args):
        self.chatlog = []
        print("#----- Chat Log Cleared -----#")

    def help(self, *args):
        """ Display a list of commands and available applications. """

        if self.available_cmds:
            dir_text = "To send a message, simply enter the message at the command prompt.\n"
            dir_text += "Enter commands in the format 'cmd [args]'. Available commands: \n"
            for cmd in self.available_cmds.keys():
                dir_text += " -" + cmd + "\n"
        else:
            dir_text = "No commands available."

        print(dir_text + "\n")

    def close(self, *args):
        self.disp_output = False  # Catch any final messages and suppress them
        self.closing = True
        print("#----- Server Shutdown -----#")

    # ----- Private Message Methods ----- #
    def runRecv(self):
        socket, AF_INET, SOCK_DGRAM, timeout = s.Socket, s.AF_INET, s.SOCK_DGRAM, s.timeout

        with socket(AF_INET, SOCK_DGRAM) as sock:
            # Socket setup
            self.socket = sock
            self.ip = sock.gethostbyname("Falafel")
            self.dest_ip = self.ip
            sock.bind((self.ip, self.port))
            sock.settimeout(1)

            print("Chat client recieving messages on IP Address {} and port {}".format(self.ip, self.port))
            print("To enter a comand, first press the enter key, then enter the command at the displayed prompt.")

            # Main loop
            while not self.closing:
                try:
                    # Check socket & parse data
                    data = sock.recvfrom(self.buflen)
                    bytearray_msg, address = data
                    src_ip, src_port = address
                    msg = bytearray_msg.decode("UTF-8")

                    # Message display & logging
                    msg_output = "\nMessage received from ip address {}, port {}:\n".format(src_ip, src_port)
                    msg_output += msg + "\n"
                    self.chatlog.append(msg_output)

                    # Account for when input is being taken
                    if self.disp_output:
                        print(msg_output)
                    else:
                        self.output_msgs.append(msg_output)

                # Allows socket's recvfrom to timeout safely
                except q.Empty:
                    continue

    def sendMessage(self, msg):
        """ Sends a message to the destination IP """
        address = (self.dest_ip, self.dest_port)
        if isinstance(msg, list):
            msg = ''.join(msg)

        # Send Message
        self.socket.sendto(msg.encode("UTF-8"), address)

if __name__ == "__main__":
    ChatClient()
