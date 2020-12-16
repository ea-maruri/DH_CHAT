
class cServer_Client:
    def __init__(self, name="", socket=None):
        self.__name = name
        self.__socket = socket
    

    def get_name(self):
        return self.__name
    

    def get_socket(self):
        return self.__socket
    

    def set_name(self, name):
        self.__name = name


    def set_socket(self, socket):
        self.__socket = socket


    def __str__(self):
        return self.get_name() + self.get_socket()
