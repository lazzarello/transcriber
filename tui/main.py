import curses
import time
import asyncio
import os
import json
from collections import deque

languages = {"english": "en", "chinese": "zh"}

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

class Pulldown:
    def __init__(self, title, options, height, width, y, x):
        self.title = title
        self.options = list(options.keys())
        self.selected_index = 0
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.window = None
        self.is_open = False

    def create_window(self, stdscr):
        self.window = stdscr.subwin(self.height, self.width, self.y, self.x)
        self.refresh()

    def toggle(self):
        self.is_open = not self.is_open
        self.refresh()

    def move_selection(self, direction):
        if self.is_open:
            self.selected_index = (self.selected_index + direction) % len(self.options)
            self.refresh()

    def get_selected(self):
        return self.options[self.selected_index]

    def refresh(self):
        if not self.window:
            return
        self.window.clear()
        self.window.box()
        
        # Draw title
        title_text = f"{self.title}: {self.options[self.selected_index]}"
        self.window.addstr(1, 2, title_text[:self.width-4])
        
        # Draw dropdown arrow
        arrow = "▼" if not self.is_open else "▲"
        self.window.addstr(1, self.width-3, arrow)
        
        # Draw options if dropdown is open
        if self.is_open:
            for i, option in enumerate(self.options):
                style = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
                self.window.addstr(i+2, 2, option[:self.width-4], style)
        
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
        self.window.nodelay(1)  # Make window non-blocking
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
        
        self.window.box()  # Redraw the border
        self.window.refresh()
        curses.doupdate()  # Force an immediate screen update

async def start_transcription(language_pulldown):
    selected_language = language_pulldown.get_selected()
    message = {"event": "on", "type": "transcribe", "language": languages[selected_language]}
    return json.dumps(message)  # Convert to proper JSON string

async def stop_transcription():
    message = {"event": "off", "type": "transcribe"}
    return json.dumps(message)

async def receive_messages(reader, message_box):
    async def refresh_loop():
        while True:
            message_box.refresh()
            await asyncio.sleep(0.1)  # 100ms refresh rate
    
    refresh_task = asyncio.create_task(refresh_loop())
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8')
            message_box.add_message(f"Received: {message}")
    except ConnectionError:
        message_box.add_message("Peer disconnected")
    finally:
        refresh_task.cancel()
        try:
            await refresh_task
        except asyncio.CancelledError:
            pass

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
    stdscr.nodelay(1)  # Make the main screen non-blocking
    
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
    
    # Create language pulldown
    language_pulldown = Pulldown(
        title="Language",
        options=languages,
        height=len(languages) + 3,  # +3 for border and title
        width=20,
        y=height-14,  # Same height as button
        x=(width-20)//2 - 25  # 25 pixels to the left of button
    )
    language_pulldown.create_window(stdscr)
    
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
    message_container = {'current': await start_transcription(language_pulldown)}

    async def handle_input():
        while True:
            try:
                key = stdscr.getch()
                if key == ord(' '):  # Space bar pressed
                    if not language_pulldown.is_open:  # Only allow recording if pulldown is closed
                        button.toggle(True)
                        message_container['current'] = await start_transcription(language_pulldown)
                        event.set()
                        message_box.add_message("Recording started")
                        
                        # Keep checking until space is released
                        stdscr.nodelay(1)
                        while True:
                            key = stdscr.getch()
                            if key == ord(' '):  # Space bar released
                                button.toggle(False)
                                message_container['current'] = await stop_transcription()
                                event.set()
                                message_box.add_message("Recording stopped")
                                break
                            await asyncio.sleep(0.01)
                        stdscr.nodelay(0)
                elif key == ord('\t'):  # Tab key to toggle pulldown
                    language_pulldown.toggle()
                elif key == curses.KEY_UP and language_pulldown.is_open:
                    language_pulldown.move_selection(-1)
                elif key == curses.KEY_DOWN and language_pulldown.is_open:
                    language_pulldown.move_selection(1)
                elif key == ord('\n') and language_pulldown.is_open:  # Enter key
                    language_pulldown.toggle()
                    selected_language = language_pulldown.get_selected()
                    message_box.add_message(f"Selected language: {selected_language}")
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
