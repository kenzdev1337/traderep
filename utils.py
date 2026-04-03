import mysql.connector

class Database():
    def __init__(self, username, password, hostname, port, database):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port
        self.database = database

        self.db = None

    def connect(self):
        self.db = mysql.connector.connect(host=self.hostname, port=self.port, username=self.username, password=self.password, database=self.database)
    
    def fetch(self, request, count):
        cursor = self.db.cursor()
        cursor.execute(request)
        result = cursor.fetchmany(count)
        result = [data[0] for data in result]
        return result
    
    def push(self, request):
        cursor = self.db.cursor()
        cursor.execute(request)
        self.db.commit()

    def execute(self, request):
        cursor = self.db.cursor()
        cursor.execute(request)

    def fetchall(self, request):
        cursor = self.db.cursor()
        cursor.execute(request)
        result = cursor.fetchall()
        result = [data[0] for data in result]
        return result