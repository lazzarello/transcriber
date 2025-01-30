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
            print(f"\nReceived: {message}")
            print("> ", end='', flush=True)
    except ConnectionResetError:
        print("\nServer disconnected")

def send_messages(conn):
    try:
        while True:
            message = input("> ")
            conn.send(message.encode('utf-8'))
    except (BrokenPipeError, ConnectionResetError):
        print("\nConnection lost")

conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
conn.connect(f'{os.getcwd()}/../engine/my_socket.sock')

print("Connected to server. Type messages and press Enter to send. Ctrl+C to quit.")

receive_thread = threading.Thread(target=receive_messages, args=(conn,))
send_thread = threading.Thread(target=send_messages, args=(conn,))

receive_thread.daemon = True
send_thread.daemon = True

try:
    receive_thread.start()  # Start threads before joining
    send_thread.start()
    
    receive_thread.join()
    send_thread.join()
except KeyboardInterrupt:
    print("\nDisconnecting...")
finally:
    conn.close()
