from app import App
import threading


class ChatClient(App):

    def __init__(self, ip='0.0.0.0', port=69, send_queue=None):
        super(ChatClient, self).__init__(app_id=port, send_queue=send_queue)
        self.clientlog = []
        self.buflen = 65500
        self.lastdest = ('0.0.73.73', 69)

        # Socket setup
        self.socket.bind((ip, port))
        self.socket.settimeout(self.socket.timeout)
        print("Chat Client started on IP Address {}, port {}".format(ip, port))

        # Run sending & recieving threads
        threading.Thread(target=self.sendInterface).start()
        threading.Thread(target=self.recvInterface).start()

    def sendMessage(self, msg, dest_ip, dest_port=69):
        """ Sends a message to the destination IP """
        address = (dest_ip, dest_port)
        if isinstance(msg, list):
            msg = ''.join(msg)

        # Send Message
        self.socket.sendto(msg.encode("UTF-8"), address)

        # Display and log on server
        self.clientlog.append(msg)
        print(msg)

    def sendInterface(self):
        while True:
            msg = input('Enter Msg: ')

            if msg:
                self.sendMessage()

    def recvInterface(self):
        while True:
            try:
                # Check socket & parse data
                data = self.socket.recvfrom(self.buflen)
                bytearray_msg, address = data
                src_ip, src_port = address
                msg = bytearray_msg.decode("UTF-8")

                # Message display & logging
                print("\nMessage received from ip address {}, port {}:".format(src_ip, src_port))
                print(msg)
                self.clientlog.append(msg)

            # Allows socket's recvfrom to timeout safely
            except RuntimeError:
                continue

if __name__ == "__main__":
    ChatClient()
