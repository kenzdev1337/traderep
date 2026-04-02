import mysql.connector

class Databse():
    def __init__(self, username, password, hostname, port):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port

    def connect(self):
        mysql.connector.connect(host=f"{self.hostname}:{self.username}", username=self.username, password=self.password)
