import socket
import os
# import sys

command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.connect(('localhost', 5004))
session_token = "INIT"


def send_message(message):
    command_socket.send(message)
    msg = command_socket.recv(2048)
    command_socket.send(session_token)
    msg = command_socket.recv(2048)

    return msg
    
def print_manual():
    print 'List of instructions:'
    print '- USER <username> : login, password will be asked'
    print '- RETR <file_name> : Download file'
    print '- RNTO <file_name> : Change file name'
    print '- STOR <file_name> : Upload file'
    print '- DELE <file_name> : Delte file'
    print '- RMD <directory_name> : Delete directory'
    print '- MKD <directory_name> : Make directory'
    print '- PWD : Get current working directory'
    print '- CWD <path> : change current working directory'
    print '- LIST : Directory listing'
    print '- QUIT : Exit from application'

print 'Welcome to FTP'
print_manual()
l=''

while True:
    cmd = raw_input("Enter command: ")
    
    if cmd.split(' ')[0] in ['USER','RETR','RNTO','DELE','RMD','MKD','PWD','CWD','LIST', 'QUIT']:
        msg = send_message(cmd)

        # if cmd == "QUIT":

        #     break

        response_code = msg.split(' ')[0]
        # print response_code

        if response_code == "151":
            cwd = os.getcwd()
            filename = cwd + '/' + cmd.split(' ')[1]
            if os.path.isfile(filename):
                size = os.path.getsize(filename)
                f = open(filename, 'rb')
                ukr = str(size)
                ukr2 = int(size)
                # namafile = "file_name : " + filename + '\r\n'
                # filesize = "file_size : " + ukr + '\r\n'
                # print namafile + filesize
                # print l
                uploaded = 0
                tmp = ''
                while(uploaded < ukr2):
                    tmp +=f.read(512)
                    uploaded = len(tmp)
                    # print str(uploaded)+'<'+ukr
                command_socket.send(ukr+'\r\n'+tmp)
                f.close()
            else:
                self.client.send("450 File doesn't exist.")

        if response_code == "331":
            # need to send password
            cmd = raw_input("Enter password: ")
            msg = send_message("PASS " + cmd)
            if msg.split(' ')[0] == "230":
                # if login success, receive and save the session_token
                token = command_socket.recv(2048)
                session_token = token

        if response_code == "221":
            command_socket.close()
            # sys.exit()
            break

        if response_code == "226":
            filename = cmd.split(' ')[1]
            f = open(filename,'wb')
            f.write(msg)
            size = msg.split('\r\n')[1]
            size2 = int(size)- 2048
            downloaded = 0
            tmp = ''
            while (downloaded < size2):
                tmp += command_socket.recv(1024)
                downloaded = len(tmp)
            f.write(tmp)
            f.close()
            fo = open(filename)
            output = []
            for line in fo:
                if not "226" in line:
                    if not size in line:
                        output.append(line)
            fo.close()
            fo = open(filename, 'w')
            fo.writelines(output)
            fo.close()
            print "Done Receiving"

        # else if cmd == "QUIT":
        #     break

        else:
            print msg
    else:
        print "Command salah."
print "221 Goodbye."
command_socket.close()