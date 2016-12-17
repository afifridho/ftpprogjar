#!/usr/bin/env python
#http://ilab.cs.byu.edu/python/threadingmodule.html 
import select
import socket
import sys
import threading
import uuid
import datetime

#here is default configuration
config = {'HOST': 'localhost', 'PORT': 5000, 'USERNAME': 'username', 'PASSWORD': 'password'}
sessions = {}

#list of commands that need authentication
commands_need_authentication = {"PWD", "CWD"}

#list of commands that must be as guest (not authenticated)
commands_need_guest = {"USER", "PASS"}

#read .env file and store it to config dictionary
def read_env():
    lines = [line.rstrip('\n') for line in open('.env')]
    for line in lines:
        stripped_line = line.split('=')
        config[stripped_line[0]] = stripped_line[1]

def create_session():
    session_id = str(uuid.uuid1())
    sessions[session_id] = datetime.datetime.now()
    return session_id

def auth(session_id):
    stored_session_id = sessions.get(session_id)
    if (stored_session_id == None):
        return False
    else:
        return True

def destroy_session(session_id):
    if (auth(session_id)):
        del sessions[session_id]

class Server:
    def __init__(self):
        self.host = config['HOST']
        self.port = int(config['PORT'])
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def open_socket(self):        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host,self.port))
        self.server.listen(5)
        
    def run(self):
        self.open_socket()
        input = [self.server, sys.stdin]
        running = 1
        print "Server is running on " + config['HOST'] + ":" + config['PORT']
        while running:
            inputready,outputready,exceptready = select.select(input,[],[])

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    c = Client(self.server.accept())
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0

        # close all threads

        self.server.close()
        for c in self.threads:
            c.join()

class Client(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024

    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)
            print 'recv: ', self.address, data
            token = self.getToken()
            if data:
                func = getattr(self, data.split(' ')[0])
                if data.split(' ')[0] in commands_need_guest:
                    if self.authenticate(token):
                        self.client.send("Need to be a guest")
                        continue

                if data.split(' ')[0] in commands_need_authentication:
                    if not self.authenticate(token):
                        self.client.send("Need authentication")
                        continue
                func(data)
                # self.client.send(data)

            else:
                self.client.close()
                running = 0

    def getToken(self):
        self.client.send("350 Send your token")
        token = self.client.recv(2048)
        return token

    def authenticate(self, token):
        if auth(token):
            return True
        else:
            return False

    def USER(self, cmd):
        cmds = cmd.split(' ')
        if (cmds[1] != config['USERNAME']):
            self.client.send("430 Invalid username")
        else:
            self.client.send("331 Please specify the password.")

    def PASS(self, cmd):
        cmds = cmd.split(' ')
        if (cmds[1] != config['PASSWORD']):
            self.client.send("430 Invalid password")
        else:
            session_id = create_session()
            self.client.send("230 Login successful.")
            self.client.send(session_id)

    def CWD(self, cmd):
        print "directory changed"
        self.client.send("250 OK.")

if __name__ == "__main__":
    read_env()
    s = Server()
    s.run()
