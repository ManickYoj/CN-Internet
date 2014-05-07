import queue as q
import threading as t


class ChatServer(object):

    def __init__(self, port=69, ip=None):
        # Initilize variables
        self.serverlog = []
        self.ips = []
        self.buflen = 65500
        self.ip = ip
        self.port = port

        # Thread control booleans
        self.exit = False
        self.disp_output = True
        self.output_msgs = []

        # UI Setup
        self.available_cmds = {'exit': self.exit, 'help': self.help}

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
            print("\n")

            cmd = input('--> Enter Cmd: ')
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

        print(dir_text + "\n")

    def exit(self, *args):


    # ----- Private Message Methods ----- #
    def runServer(self):
        # TODO: Need a with statement/instatiation here!
        
        # Socket setup
        self.socket.bind((self.ip, self.port))
        self.socket.settimeout(1)
        print("Chat Server started on IP Address {}, port {}".format(self.ip, self.port))
        print("To enter a comand, first press the enter key, then enter the command at the displayed prompt.")

        # Main loop
        while not self.exit:
            try:
                # Check socket & parse data
                data = self.socket.recvfrom(self.buflen)
                bytearray_msg, address = data
                src_ip, src_port = address
                msg = bytearray_msg.decode("UTF-8")

                # Message display & logging
                msg_output = "\nMessage received from ip address {}, port {}:\n".format(src_ip, src_port)
                msg_output += msg + "\n"
                self.serverlog.append(msg_output)

                # Account for when input is being taken
                if self.disp_output:
                    print(msg_output)
                else:
                    self.new_msgs.append(msg_output)

                # Add new users and relay messages
                if src_ip not in self.ips:
                    self.ips.append(src_ip)
                self.relayMessage(msg, src_ip)

            # Allows socket's recvfrom totimeout safely
            except q.Empty:
                continue

    def sendMessage(self, msg, dest_ip, dest_port=69):
        """ Sends a message to the destination IP """
        address = (dest_ip, dest_port)
        if isinstance(msg, list):
            msg = ''.join(msg)

        # Send Message
        self.socket.sendto(msg.encode("UTF-8"), address)

    def relayMessage(self, msg, src_ip):
        """ Repeates a message from the given source IP, if valid. """
        if len(msg) >= self.buflen:
            self.sendMessage("Message was too long and has not been sent.", src_ip)
        else:
            for ip in self.ips:
                self.sendMessage(msg, ip)

if __name__ == "__main__":
    ChatServer()
