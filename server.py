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

#read .env file and store it to config dictionary
def read_env():
    lines = [line.rstrip('\n') for line in open('.env')]
    for line in lines:
        stripped_line = line.split('=')
        config[stripped_line[0]] = stripped_line[1]

def create_session():
    session_id = uuid.uuid1()
    sessions[session_id] = datetime.datetime.now()

def auth(session_id):
    if (sessions[session_id]):
        return True
    else:
        return False

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
            if data:
                self.client.send(data)
            else:
                self.client.close()
                running = 0

if __name__ == "__main__":
    read_env()
    s = Server()
    s.run()
