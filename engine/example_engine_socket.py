import socket
import os
import threading

def receive_messages(conn):
    try: 
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(message)
    except ConnectionResetError:
        print("Client disconnected")

def send_messages(conn):
    try:
        while True:
            message = input("> ")
            conn.send(message.encode('utf-8'))
    except (BrokenPipeError, ConnectionResetError):
        print("\nConnection lost")

socket_path = f'{os.getcwd()}/my_socket.sock'
if os.path.exists(socket_path):
    os.remove(socket_path)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socket_path)
server.listen(1)

print("Server started, waiting for connection...")
while True:
    conn, addr = server.accept()
    print("Client connected")

    receive_thread = threading.Thread(target=receive_messages, args=(conn,))
    send_thread = threading.Thread(target=send_messages, args=(conn,))

    receive_thread.daemon = True
    send_thread.daemon = True

    receive_thread.start()  # Start threads before joining
    send_thread.start()
    
    receive_thread.join()
    send_thread.join()
    conn.close()
