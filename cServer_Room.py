
class cServer_Room:
    def __init__(self, id: str, creator):
        self.__id = id
        self.__creator = creator
        self.__list_of_clients = list() #List of strings

        # Creator is a client cServer_Client(name, socket)
        self.__list_of_clients.append(creator)
        self.__list_of_clients.clear()
        

    def get_id(self):
        return self.__id


    def get_creator(self):
        return self.__creator
    

    def get_list_of_clients(self):
        return self.__list_of_clients
   
    
    def get_list_of_names(self):
        clients = ""
        for client in self.get_list_of_clients():
            if client:
                clients += client.get_name() + ","

        return clients[:-1]
    
    
    def __str__(self):
        if self.get_creator():
            return "Room: " + self.get_id() + "\n\tCreator: " + self.get_creator().get_name() + "\n\tClients: " + self.get_list_of_names()
        else:
            return "Room: " + self.get_id() + "\n\tCreator: " + "NONE" + "\n\tClients: " + self.get_list_of_names()