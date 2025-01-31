import curses
import time
import asyncio
import os
from collections import deque

class Button:
    def __init__(self, title, height, width, y, x):
        self.title = title
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.pressed = False
        self.window = None

    def create_window(self, stdscr):
        self.window = stdscr.subwin(self.height, self.width, self.y, self.x)
        self.refresh()

    def toggle(self, pressed):
        self.pressed = pressed
        self.refresh()

    def refresh(self):
        if not self.window:
            return
        self.window.clear()
        style = curses.A_REVERSE if self.pressed else curses.A_NORMAL
        centered_x = (self.width - len(self.title)) // 2
        self.window.addstr(0, centered_x, self.title, style)
        self.window.refresh()

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

async def start_transcription():
    message = {"event": "on", "type": "transcribe"}
    return message

async def stop_transcription():
    message = {"event": "off", "type": "transcribe"}
    return message

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

async def send_messages(writer, message_box, event, message_container):
    try:
        while True:
            await event.wait()
            writer.write(str(message_container['current']).encode('utf-8'))
            await writer.drain()
            message_box.add_message(f"Sent: {message_container['current']}")
            event.clear()
    except ConnectionError:
        message_box.add_message("Connection lost")

async def main(stdscr):
    # Initialize curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Create button above message box
    button = Button(
        title="TRANSCRIBE",
        height=1,
        width=20,
        y=height-14,  # 2 lines above message box
        x=(width-20)//2  # centered
    )
    button.create_window(stdscr)
    
    # Create message box in the bottom half of the screen
    message_box = MessageBox(
        height=10,
        width=width-4,
        y=height-12,
        x=2
    )
    message_box.create_window(stdscr)
    
    # Connect to socket
    socket_path = f'{os.getcwd()}/../engine/my_socket.sock'
    reader, writer = await asyncio.open_unix_connection(socket_path)
    
    message_box.add_message("Connected. Press SPACE to start/stop transcription. Ctrl+C to quit.")

    # Create an event for communication between input and send_messages
    event = asyncio.Event()
    # Create a container for sharing the current message between coroutines
    message_container = {'current': await start_transcription()}

    async def handle_input():
        while True:
            try:
                key = stdscr.getch()
                if key == ord(' '):  # Space bar
                    button.toggle(True)
                    message_container['current'] = await start_transcription()
                    event.set()
                    
                    # Wait for key release
                    while True:
                        key = stdscr.getch()
                        if key == ord(' '):
                            button.toggle(False)
                            message_container['current'] = await stop_transcription()
                            event.set()
                            break
                        await asyncio.sleep(0.01)
            except Exception as e:
                message_box.add_message(f"Input error: {str(e)}")
            await asyncio.sleep(0.01)

    try:
        await asyncio.gather(
            receive_messages(reader, message_box),
            send_messages(writer, message_box, event, message_container),
            handle_input()
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
