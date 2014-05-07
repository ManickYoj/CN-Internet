import GlobalVars as g
import ServerFunctions as s

AdminCommands = {"clearServerLog":"clearServerLog","printServerLog":"printServerLog","banUser":"banUser", "liftBan":"liftBan","dispBannedIPs":"dispBannedIPs"}

def parseCommandString(command, argument, source_IP):
	if command==AdminCommands['clearServerLog']:
		clearServerLog(source_IP);
	elif command==AdminCommands['printServerLog']:
		printServerLog(source_IP);
	elif command==AdminCommands['banUser']:
		banUser(source_IP, argument);
	elif command==AdminCommands['liftBan']:
		liftBan(source_IP, argument);
	elif command == AdminCommands['dispBannedIPs']:
		dispBannedIPs(source_IP);


def printServerLog(source_IP):
	#TODO: Make this function make sense
	ServerLog = g.ServerLog[:]
	server_log_char_len = 2+13;
	truncate_entry = 0;
	for i in range(-1,(-len(ServerLog))-1,-1):
		server_log_char_len+=6 #Account for quotes and space formatting
		server_log_char_len += len(ServerLog[i]);
		if server_log_char_len>g.client_buffer_size:
			truncate_entry = i+1;
			break;
	s.sendMessage(ServerLog[truncate_entry:],source_IP);

def clearServerLog(source_IP):
	g.ServerLog = [];
	s.sendMessage("Server log cleared.", source_IP)

def banUser(source_IP, ban_alias):
	if ban_alias is None or not ban_alias in g.IPs.keys():
		s.sendMessage("User " + str(ban_alias) + " does not exist.", source_IP);
	else:
		g.BannedIPs.append(g.IPs[ban_alias]);
		s.sendMessage("You have been banned by an admin.", g.IPs[ban_alias]);
		del g.Users[g.IPs[ban_alias]];
		del g.IPs[ban_alias];
		s.sendMessage("User " + str(ban_alias) + " successfully banned.", source_IP);
		

def liftBan(source_IP, ban_IP):
	if ban_IP in g.BannedIPs:
		g.BannedIPs.remove(ban_IP);
		s.sendMessage("Your ban has been lifted by an administrator.", ban_IP);
		s.sendMessage("Ban on " + str(ban_IP) + " has been lifted.",source_IP);
	else:
		s.sendMessage("IP " + str(ban_IP) + " is not on ban list.", source_IP);

def dispBannedIPs(source_IP):
	if not g.BannedIPs:
		s.sendMessage("No IPs are currently banned.", source_IP);
	else:
		msg = "Banned IPs: \n";
		for IP in g.BannedIPs:
			msg += IP + "\n";
		s.sendMessage(msg, source_IP);

		
