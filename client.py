import socket

command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.connect(('127.0.0.1', 5000))

session_token = "INIT"


def send_message(message):
    command_socket.send(message)
    msg = command_socket.recv(2048)
    command_socket.send(session_token)
    msg = command_socket.recv(2048)
    return msg

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
    else:
        print msg


print "221 Goodbye."
command_socket.close()