import socket
import os

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(f'{os.getcwd()}/../engine/my_socket.sock')

print("Connected to server. Type messages and press Enter to send. Ctrl+C to quit.")

try:
    while True:
        message = input("> ")
        client.send(message.encode('utf-8'))
except KeyboardInterrupt:
    print("\nDisconnecting...")
finally:
    client.close()