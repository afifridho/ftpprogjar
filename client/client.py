import socket
import os

command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.connect(('127.0.0.1', 5000))

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

    if cmd == "QUIT":
        break

    msg = send_message(cmd)
    # filename = cmd.split(' ')[1]

    response_code = msg.split(' ')[0]

    # after login, we need to enter the password
    if response_code == "331":
        # need to send password
        cmd = raw_input("Enter password: ")
        msg = send_message("PASS " + cmd)
        print msg
        if msg.split(' ')[0] == "230":
            # if login success, receive and save the session_token
            token = command_socket.recv(2048)
            session_token = token

    if response_code == "226":
        filename = cmd.split(' ')[1]
        f = open(filename,'wb')
        f.write(msg)
        # print msg
        size = msg.split('\r\n')[1]
        size2 = int(size)- 2048
        print size2 
        downloaded = 0
        tmp = ''
        while (downloaded < size2):
            tmp += command_socket.recv(1024)
            downloaded = len(tmp)
            print str(downloaded)+'<'+str(size2)
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

    # if response_code == "jebret":
    #     print "masuk gan"
    #     cwd = os.getcwd()
    #     nama_file = cwd + '/' + cmd.split(' ')[1]

    #     with open (nama_file, 'rb') as f:
    #         print "masuk if"
    #         data = ""
    #         data = f.read(1024)
    #         while data:
    #             print "masuk while"
    #             command_socket.send(data)
    #             data = f.read(1024)
    #         print data
    #     f.close()
        
    else:
        print msg


print "221 Goodbye."
command_socket.close()