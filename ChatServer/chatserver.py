from app import App
import queue as q


class ChatServer(App):

    def __init__(self, port=69, send_queue=None, ip='0.0.73.73'):
        super(ChatServer, self).__init__(app_id=port, send_queue=send_queue)
        self.serverlog = []
        self.ips = []
        self.buflen = 65500

        # Socket setup
        self.socket.bind((ip, port))
        self.socket.settimeout(1)
        print("Chat Server started on IP Address {}, port {}".format(ip, port))

        # Main loop
        while True:
            try:
                # Check socket & parse data
                data = self.socket.recvfrom(self.buflen)
                bytearray_msg, address = data
                src_ip, src_port = address
                msg = bytearray_msg.decode("UTF-8")
                print("test")

                # Message display & logging
                print("\nMessage received from ip address {}, port {}:".format(src_ip, src_port))
                print(msg)
                self.serverlog.append(msg)

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

        # Display and log on server
        self.serverlog.append(msg)
        print(msg)

    def relayMessage(self, msg, src_ip):
        if len(msg) >= self.buflen:
            self.sendMessage("Message was too long and has not been sent.", src_ip)
        else:
            for ip in self.ips:
                self.sendMessage(msg, ip)

if __name__ == "__main__":
    ChatServer()


class User(object):

    def __init__(self):
        print("User")
