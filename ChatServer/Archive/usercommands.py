import serverfunctions as s
import admincommands as a
import user as u

Commands = {"set_name": "SETNAME", "disp_users": "USERS", "get_help": "HELP", "connect": "CONNECT","disconnect": "DISCONNECT", "admin": "ADMIN"}

#------------User Accessible Commands/Command Parsing------------#
def parseCommandString(message, source_IP, source_port):
	""" Given a command message, calls the corresponding function and passes any arguments """
	#TODO: Move all user commands to a seperate class
	if message is not None and not message=="":
		message = message.split()
		command = message[0];
	else: return;
	if len(message)>1:
		argument = message[1];
	else: argument=None;


	#Only allow logged in users to execute commands other than \connect
	if not source_IP in g.Users and not command==Commands['connect']:
		s.requestConnect(source_IP, source_port);
		return;

	if command in a.AdminCommands:
		if g.Users[source_IP].isAdmin:
			a.parseCommandString(command, argument, source_IP);
			return;
		else:
			s.sendMessage("You do not have access to this command.", source_IP);
			return;

	#Parse Commands
	if command == Commands['set_name']:
		if argument is not None:
			setName(argument, source_IP);
		else:
			s.sendMessage("Invalid input. Please enter a valid name in format /setName [name]",source_IP);
	elif command == Commands['connect']:
		if argument is not None:
			connect(argument, source_IP, source_port);
		else:
			s.sendMessage("Invalid input. Please enter a valid name in format /connect [name]",source_IP,source_port);
	elif command == Commands['admin']:
		if argument is not None:
		       admin(argument, source_IP);
		else:
			s.sendMessage("Invalid password entry. Please enter a valid entry in format /admin [password]",source_IP);
	elif command == Commands['disconnect']:
		disconnect(source_IP);
	elif command == Commands['disp_users']:
		dispUsers(source_IP);
	elif command == Commands['get_help']:
		sendHelp(source_IP);
	else:
		s.sendMessage("INVALID COMMAND.", source_IP, source_port);
		

def admin(pw, source_IP):
	""" Toggle admin status on user """
	#TODO: add password hashing
	if pw==g.admin_pw:
		s.sendMessage(g.Users[source_IP].toggleAdmin(), source_IP);
	else:
		s.sendMessage("Invalid admin login.",source_IP);

def invisible(source_IP):
	""" Toggle invisible status on user """
	#TODO: make invisibility actually have an effect
	s.sendMessage(g.Users[source_IP].toggleInvisible(),source_IP);

		
def connect(name, source_IP, source_port):
	""" Creates a new user session """
	if g.Users.get(source_IP) is not None:
		renewConnection(source_IP);
	elif source_IP in g.BannedIPs:
	    s.sendMessage("You are currently banned from the server.",source_IP,source_port);
	elif not name in g.IPs.keys():
		g.Users[source_IP] = u.User(name, source_port);
		g.IPs[name] = source_IP;
		s.serverWelcome(source_IP);
	else:
		s.sendMessage("Name already taken.",source_IP);

def disconnect(source_IP):
	""" Delete a user session """
	del g.IPs[g.Users[source_IP].alias];
	del g.Users[source_IP];
	s.sendMessage("Successfully logged out.", source_IP);
	
def setName(name, source_IP):
	""" Resets a client's alias """
	if not name in g.IPs.keys():
		del g.IPs[g.Users[source_IP].alias];
		g.Users[source_IP].alias = name;
		g.IPs[name] = source_IP;
	else:
		s.sendMessage("Name already taken.", source_IP);

def dispUsers(dest_IP):
	""" Sends a list of all logged in user aliases """
	#TODO: Implement invisibility
	message = "Users currently in chat: \n"
	for user in g.IPs.keys():
		message += user + "\n"
	s.sendMessage(message, dest_IP);
		
def sendHelp(dest_IP):
	#TODO: Add descriptions of functions
	""" Sends a message to the destination IP listing (and ideally explaining) functions available to them """
	command_string = "";
	for command in Commands.values():
		command_string += "/" + command + ", "
	help_message = "Available Commands: " + command_string[:-2];
	s.sendMessage(help_message, dest_IP);

	if g.Users[dest_IP].isAdmin:
		admin_command_string = "Available Admin Commands:"
		for command in a.AdminCommands.values():
			admin_command_string += command + ", ";
		s.sendMessage(admin_command_string, dest_IP);

	
def renewConnection(dest_IP):
	""" Not Yet Implemented """
	#TODO: Implement
