import socket

command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.connect(('127.0.0.1', 5000))

session_token = "INIT"


def send_message(message):
    # data=''
    command_socket.send(message)
    msg = command_socket.recv(2048)
    # print "sent ke 2"
    command_socket.send(session_token)
    # print "masuk msg 2"
    msg = command_socket.recv(2048)
    # while msg:
    #     print "masuk while"
    #     tmp = command_socket.recv(2048)
    #     if tmp == '':
    #         print "masuk if"
    #         break
        # data=msg+tmp
        # print "================"
        # msg+=data

    # print msg
    return msg

def print_manual():
    print 'List of instructions:'
    print '- USER <username> : login, password will be asked'
    print '- PWD : Get current working directory'
    print '- CWD <path> : change current working directory'
    print '- QUIT : Exit from application'

print 'Welcome to FTP'
print_manual()

while True:
    cmd = raw_input("Enter command: ")

    if cmd == "QUIT":
        break

    msg = send_message(cmd)

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

    # if response_code = ""
    else:
        print msg


print "221 Goodbye."
command_socket.close()