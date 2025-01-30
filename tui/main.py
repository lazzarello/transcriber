import curses
import time
import asyncio
import os
from collections import deque

class MessageBox:
    def __init__(self, height, width, y, x):
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.messages = deque(maxlen=height)
        self.window = None

    def create_window(self, stdscr):
        self.window = stdscr.subwin(self.height + 2, self.width + 2, self.y, self.x)
        self.window.box()
        self.refresh()

    def add_message(self, message):
        # Split long messages into multiple lines
        while len(message) > self.width:
            self.messages.append(message[:self.width])
            message = message[self.width:]
        self.messages.append(message)
        self.refresh()

    def refresh(self):
        if not self.window:
            return
        # Clear the content area (not the border)
        for i in range(self.height):
            self.window.addstr(i + 1, 1, " " * self.width)
        
        # Print messages
        for i, msg in enumerate(self.messages):
            if i < self.height:
                self.window.addstr(i + 1, 1, msg[:self.width])
        
        self.window.refresh()

async def receive_messages(reader, message_box):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8')
            message_box.add_message(f"Received: {message}")
    except ConnectionError:
        message_box.add_message("Peer disconnected")

async def send_messages(writer, message_box):
    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(
                None, lambda: input("> ")
            )
            writer.write(message.encode('utf-8'))
            await writer.drain()
            message_box.add_message(f"Sent: {message}")
    except ConnectionError:
        message_box.add_message("Connection lost")

async def main(stdscr):
    # Initialize curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()
    
    # Create message box in the bottom half of the screen
    height, width = stdscr.getmaxyx()
    message_box = MessageBox(
        height=10,  # Height of message area
        width=width-4,  # Width of message area
        y=height-12,  # Position from top
        x=2  # Position from left
    )
    message_box.create_window(stdscr)
    
    # Connect to socket
    socket_path = f'{os.getcwd()}/../engine/my_socket.sock'
    reader, writer = await asyncio.open_unix_connection(socket_path)
    
    message_box.add_message("Connected. Type messages and press Enter to send. Ctrl+C to quit.")
    
    try:
        await asyncio.gather(
            receive_messages(reader, message_box),
            send_messages(writer, message_box)
        )
    finally:
        writer.close()
        await writer.wait_closed()

def run():
    try:
        curses.wrapper(lambda stdscr: asyncio.run(main(stdscr)))
    except KeyboardInterrupt:
        print("\nDisconnecting...")

if __name__ == "__main__":
    run()