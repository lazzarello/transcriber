import urwid
import asyncio
import os
import json
from collections import deque

languages = {"english": "en", "chinese": "zh"}

class TranscribeButton(urwid.Button):
    def __init__(self, label):
        super().__init__("")
        btn = urwid.AttrWrap(urwid.SelectableIcon(label, 2), 'button', 'button_focus')
        self._w = btn
        self.pressed = False

    def toggle(self, pressed):
        self.pressed = pressed
        self._w.set_attr_map({None: 'button_pressed' if pressed else 'button'})

class LanguagePulldown(urwid.WidgetWrap):
    def __init__(self, title, options):
        self.title = title
        self.options = list(options.keys())
        self.selected_index = 0
        self.is_open = False
        
        self.button = urwid.Button(self._get_label())
        urwid.connect_signal(self.button, 'click', lambda _: self.toggle())
        
        self.option_widgets = []
        for option in self.options:
            opt_btn = urwid.Button(option)
            urwid.connect_signal(opt_btn, 'click', lambda _, o=option: self._select_option(o))
            self.option_widgets.append(urwid.AttrMap(opt_btn, None, focus_map='reversed'))
        
        self.pile = urwid.Pile([self.button])
        super().__init__(self.pile)

    def _get_label(self):
        arrow = "▼" if not self.is_open else "▲"
        return f"{self.title}: {self.options[self.selected_index]} {arrow}"

    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.pile.contents = [(self.button, ('pack', None))] + \
                               [(w, ('pack', None)) for w in self.option_widgets]
        else:
            self.pile.contents = [(self.button, ('pack', None))]
        self.button.set_label(self._get_label())

    def _select_option(self, option):
        self.selected_index = self.options.index(option)
        self.is_open = False
        self.button.set_label(self._get_label())
        self.pile.contents = [(self.button, ('pack', None))]

    def get_selected(self):
        return self.options[self.selected_index]

class MessageBox(urwid.WidgetWrap):
    def __init__(self):
        self.messages = deque(maxlen=10)
        self.listbox = urwid.ListBox(urwid.SimpleListWalker([]))
        self.box = urwid.LineBox(self.listbox)
        super().__init__(self.box)

    def add_message(self, message):
        self.messages.append(message)
        self.listbox.body[:] = [urwid.Text(msg) for msg in self.messages]
        self.listbox.set_focus(len(self.listbox.body) - 1)

async def start_transcription(language_pulldown):
    selected_language = language_pulldown.get_selected()
    message = {"event": "on", "type": "transcribe", "language": languages[selected_language]}
    return json.dumps(message)

async def stop_transcription():
    message = {"event": "off", "type": "transcribe"}
    return json.dumps(message)

class TranscriberUI:
    def __init__(self):
        self.message_box = MessageBox()
        self.button = TranscribeButton("TRANSCRIBE")
        # Connect the button's click signal to our handler
        urwid.connect_signal(self.button, 'click', self._on_button_click)
        self.language_pulldown = LanguagePulldown("Language", languages)
        
        # Layout
        header = urwid.Columns([
            ('pack', self.language_pulldown),
            ('pack', urwid.Text("  ")),  # spacing
            ('pack', self.button),
        ])
        
        main_layout = urwid.Pile([
            ('pack', header),
            ('pack', urwid.Divider()),
            self.message_box
        ])
        
        self.main_widget = urwid.Padding(main_layout, left=2, right=2)
        self.loop = None
        self.reader = None
        self.writer = None
        self.event = asyncio.Event()
        self.message_container = {'current': None}

    async def connect(self):
        socket_path = f'{os.getcwd()}/../engine/my_socket.sock'
        self.reader, self.writer = await asyncio.open_unix_connection(socket_path)
        self.message_box.add_message("Connected. Press SPACE to start/stop transcription. Q to quit.")

    def _on_button_click(self, button):
        if not self.language_pulldown.is_open:
            if not self.button.pressed:
                self.button.toggle(True)
                asyncio.create_task(self._handle_transcription_start())
            else:
                self.button.toggle(False)
                asyncio.create_task(self._handle_transcription_stop())

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key == ' ':
            if not self.language_pulldown.is_open:
                if not self.button.pressed:
                    self.button.toggle(True)
                    asyncio.create_task(self._handle_transcription_start())
                else:
                    self.button.toggle(False)
                    asyncio.create_task(self._handle_transcription_stop())

    async def _handle_transcription_start(self):
        self.message_container['current'] = await start_transcription(self.language_pulldown)
        self.event.set()
        self.message_box.add_message("Recording started")

    async def _handle_transcription_stop(self):
        self.message_container['current'] = await stop_transcription()
        self.event.set()
        self.message_box.add_message("Recording stopped")

    def run(self):
        # Get the current event loop
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        
        # Run initial connection
        event_loop.run_until_complete(self.connect())
        
        # Set up urwid event loop
        urwid_loop = urwid.AsyncioEventLoop(loop=event_loop)
        self.loop = urwid.MainLoop(
            self.main_widget,
            palette=[
                ('button', 'black', 'white'),
                ('button_focus', 'white', 'dark blue'),
                ('button_pressed', 'white', 'dark red'),
                ('reversed', 'standout', ''),
            ],
            event_loop=urwid_loop,
            unhandled_input=self.handle_input
        )

        self.loop.screen.set_terminal_properties(colors=256)
        
        # Schedule our async tasks
        def schedule_async_tasks():
            event_loop.create_task(self.receive_messages())
            event_loop.create_task(self.send_messages())
        
        self.loop.event_loop.alarm(0, schedule_async_tasks)
        
        try:
            self.loop.run()
        finally:
            if self.writer:
                event_loop.run_until_complete(self.writer.wait_closed())

    async def receive_messages(self):
        try:
            while True:
                data = await self.reader.read(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                self.message_box.add_message(f"Received: {message}")
        except ConnectionError:
            self.message_box.add_message("Peer disconnected")

    async def send_messages(self):
        try:
            while True:
                await self.event.wait()
                self.writer.write(str(self.message_container['current']).encode('utf-8'))
                await self.writer.drain()
                self.message_box.add_message(f"Sent: {self.message_container['current']}")
                self.event.clear()
        except ConnectionError:
            self.message_box.add_message("Connection lost")

def run():
    try:
        ui = TranscriberUI()
        ui.run()
    except KeyboardInterrupt:
        print("\nDisconnecting...")

if __name__ == "__main__":
    run()
