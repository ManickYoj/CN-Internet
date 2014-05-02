import app

class ChatServer(App):
	def __init__(self, ip='0.0.73.73', port=69):
		self.serverlog = []
		self.ips = []
		self.buflen = 65500

		# Socket setup
		socket.bind((IP,port))
		sock.settimeout(timeout)
		print ("Chat Server started on IP Address {}, port {}".format(IP,port))

		# Main loop
		while True:
			# Check socket & parse data
			data = sock.recvfrom(self.buflen);
			bytearray_msg, address = data;
			src_ip, src_port = address;
			msg = bytearray_msg.decode("UTF-8");

			# Message display & logging
			print ("\nMessage received from ip address {}, port {}:".format(src_ip, src_port))
			print(msg);
			g.ServerLog.append(msg);

			# Add new users and relay messages
			if src_ip not in self.ips:
				ips.append(src_ip)
			self.relayMessage(msg, src_ip)

		# Allows socket's recvfrom totimeout safely
		except RuntimeError:
			continue

def sendMessage(self, msg, dest_ip, dest_port = 69):
	""" Sends a message to the destination IP """
	address = (dest_ip, dest_port)
	if isinstance(message,list):
		msg = ''.join(message);

	# Send Message
	socket.sendto(msg.encode("UTF-8"), address)

	# Display and log on server
	self.serverlog.append(msg)
	print(msg);

def relayMessage(msg, src_ip):
	if len(msg) >= self.buflen:
		self.sendMessage("Message was too long and has not been sent.", src_ip)
	else:
		for ip in self.ips:
			self.sendMessage(msg, ip)

if __name__ == "__main__":
	Chat_Server();

class User(object):
	def __init__(self):
		print("User")