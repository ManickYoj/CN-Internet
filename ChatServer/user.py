from GlobalVars import default_client_port

class User:

    def __init__(self, alias, port=default_client_port):
        self.alias = alias;
        self.isInvisible = False;
        self.isAdmin = False;
    
        self.messagesInTimeout=0;
        self.timeSinceActive=0;
        self.port = port

    def toggleAdmin(self):
        self.isAdmin = not self.isAdmin;
        return "Admin status: " + str(self.isAdmin);

    def toggleInvisible(self):
        self.isInvisible = not self.isInvisible;
        return "Invisibility: " + str(self.isInvisible);

