import urwid
import threading
import time

def update_time(loop, widget):
    widget.set_text(f"Time: {time.time()}")
    loop.set_alarm_in(1, update_time, widget)

def main():
    text_widget = urwid.Text("Press 'q' to quit")
    filler = urwid.Filler(text_widget, 'top')
    loop = urwid.MainLoop(filler, unhandled_input=exit_on_q)
    
    loop.set_alarm_in(1, update_time, text_widget)
    loop.run()

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

if __name__ == "__main__":
    main()
