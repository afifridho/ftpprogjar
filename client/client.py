import socket
import os

command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.connect(('127.0.0.1', 5004))

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
    print '- PWD : get current working directory'
    print '- CWD <path> : change current working directory'
    print '- LIST <path> : list all files and folders working directory'
    print '- MKD <path> : change current working directory'
    print '- RMD <path> : change current working directory'
    print '- DELE <path> : change current working directory'
    print '- RETR <path> : change current working directory'
    print '- STOR <path> : change current working directory'
    print '- RNTO <path> : change current working directory'
    print '- QUIT : Exit from application'

print 'Welcome to FTP'
print_manual()
l=''

while True:
    cmd = raw_input("Enter command: ")

    msg = send_message(cmd)

    if cmd == "QUIT":
        break

    response_code = msg.split(' ')[0]
    print response_code

    # after login, we need to enter the password
    if response_code == "STOR":
        print 'masuk tot'
        cwd = os.getcwd()
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
            uploaded = 0
            tmp = ''
            while(uploaded < ukr2):
                tmp +=f.read(512)
                uploaded = len(tmp)
                print str(uploaded)+'<'+ukr
            command_socket.send(ukr+'\r\n'+tmp)
            f.close()

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

    else:
        print msg


print "221 Goodbye."
command_socket.close()