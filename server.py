#!/usr/bin/env python
#http://ilab.cs.byu.edu/python/threadingmodule.html 
import select
import socket
import sys
import threading
import uuid
import datetime
import os

#here is default configuration
config = {'HOST': 'localhost', 'PORT': 5000, 'USERNAME': 'username', 'PASSWORD': 'password'}
sessions = {}
current_working_directory = {}
base_directory = os.getcwd()

#list of commands that need authentication
commands_need_authentication = {"PWD", "CWD", "RETR", "STOR", "RNTO", "DELE", "RMD", "MKD", "LIST"}

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
    current_working_directory[session_id] = os.getcwd()
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

            # print data[:1]

            # if data[0] == 'S':
            #     print "jebret"
            #     token = self.getToken()
            #     func('STOR', token)
            #     print "jebret cok"

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
                func(data, token)
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

    def USER(self, cmd, session_id):
        cmds = cmd.split(' ')
        if (cmds[1] != config['USERNAME']):
            self.client.send("430 Invalid username")
        else:
            self.client.send("331 Please specify the password.")

    def PASS(self, cmd, session_id):
        cmds = cmd.split(' ')
        if (cmds[1] != config['PASSWORD']):
            self.client.send("430 Invalid password")
        else:
            session_id = create_session()
            self.client.send("230 Login successful.")
            self.client.send(session_id)

    def PWD(self, cmd, session_id):
        cwd = current_working_directory[session_id]
        self.client.send("250 " + cwd)

    def CWD(self, cmd, session_id):
        cmds = cmd.split(' ')
        target_directory = cmds[1]

        if (target_directory[0] == '/'):
            # Client define absolute path
            target_directory = os.getcwd() + target_directory
        else:
            # Client define relative path
            target_directory = current_working_directory[session_id] + '/' + target_directory
        print "target directory = " + target_directory
        if os.path.isdir(target_directory):
            current_working_directory[session_id] = target_directory
            self.client.send("250 Directory changed")
        else:
            self.client.send("450 Directory doesn't exist")

    def HELP(self, cmd, session_id):
        self.client.send('214-The following commands are recognized:\r\nCWD\r\nQUIT\r\nRETR\r\nSTOR\r\nRNTO\r\nDELE\r\nRMD\r\nMKD\r\nPWD\r\nLIST\r\nHELP\r\n')

    def MKD(self, cmd, session_id):
        cwd = current_working_directory[session_id]
        print cwd
        base_directory_len = len(base_directory)
        cwd_len = len(cwd)
        dirname = cmd.split(' ')[1]
        os.mkdir(cwd+'/'+dirname)
        self.client.send("257 Directory created.")

    def RMD(self, cmd, session_id):
        cwd = current_working_directory[session_id]
        print cwd
        base_directory_len = len(base_directory)
        cwd_len = len(cwd)
        dirname = cmd.split(' ')[1]
        if os.path.isdir(dirname):
            os.rmdir(cwd+'/'+dirname)
            self.client.send("250 Directory deleted.")
        else:
            self.client.send('450 Not allowed.')

    def LIST(self, cmd, session_id):
        cwd = current_working_directory[session_id]
        data=''
        dirs = os.listdir(cwd+'/')
        for file in dirs:
            if file=='':
                break
            data+=file+'\r\n'
        self.client.send('150 Here comes the directory listing.\r\n' +data + '226 Directory send OK.')
    
    def DELE(self, cmd, session_id):
        cwd = current_working_directory[session_id]
        nama_file = cmd.split(' ')[1]
        if os.path.isfile(nama_file):
            os.remove(cwd+'/'+nama_file)
            self.client.send("250 File deleted.")
        else:
            self.client.send('450 Not allowed.')

    def RNTO(self, cmd, session_id):
    	cwd = current_working_directory[session_id]
    	source = cwd + '/' + cmd.split(' ')[1]
        if os.path.isfile(source):
            destination = cwd + '/' + cmd.split(' ')[2]
    	    os.rename(source,destination)
    	    self.client.send('250 File renamed.')
        else:
            self.client.send('450 Not allowed.')


    def RETR(self, cmd, session_id):
        cwd = current_working_directory[session_id]
        filename = cwd + '/' + cmd.split(' ')[1]

        if os.path.isfile(filename):
            size = os.path.getsize(filename)
            f = open(filename, 'rb')
            ukr = str(size)
            ukr2 = int(size)
            namafile = "file_name : " + filename + '\r\n'
            filesize = "file_size : " + ukr + '\r\n'
            print namafile + filesize
            # print l
            downloaded = 0
            tmp = ''
            while(downloaded < ukr2):
                tmp +=f.read(512)
                downloaded = len(tmp)
            # print '226 Transfer Complete\r\n'+ ukr +'\r\n' + tmp 
            self.client.send('226 Transfer Complete\r\n'+ ukr +'\r\n'+ tmp)
            f.close()

    # def STOR(self, cmd, session_id):
    #     cwd = current_working_directory[session_id]
    #     self.client.send("jebret a cok\r\n")
    #     filename = cwd + '/' + cmd.split(' ')[1]

    # def clean_file(self, cmd, session_id):
    #     yourfile = self.cleaned_data.get("your_filename_on_template", False)
    #     filetype = magic.from_buffer(yourfile.read())
    def start_datasock(self): 
        if self.pasv_mode: 
            self.datasock, addr = self.servsock.accept() 
            print 'connect:', addr 
        else: 
            self.datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            self.datasock.connect((self.dataAddr,self.dataPort))

    def stop_datasock(self): 
        self.datasock.close() 
        if self.pasv_mode: 
            self.servsock.close() 

    def STOR(self,cmd): 
        fn=os.path.join(self.cwd,cmd[5:-2]) 
        print 'Uplaoding:',fn 
        if self.mode=='I': 
            fo=open(fn,'wb') 
        else: 
            fo=open(fn,'w') 
            self.conn.send('150 Opening data connection.\r\n') 
            self.start_datasock() 
            while True: 
                data=self.datasock.recv(1024) 
                if not data: 
                    break 
                fo.write(data) 
                fo.close() 
            self.stop_datasock() 
            self.conn.send('226 Transfer complete.\r\n')



if __name__ == "__main__":
    read_env()
    s = Server()
    s.run()
