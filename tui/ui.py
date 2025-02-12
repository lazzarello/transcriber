from __future__ import annotations
import typing
import urwid

palette = [("transcribe", "default,bold", "default", "bold")]
speak = urwid.Button("Speak")
div = urwid.Divider()
# ERROR: this won't work without a function, see tutorial for pull-down menus
language = urwid.ListBox(urwid.SimpleListWalker([]))
sound_source = urwid.ListBox(urwid.SimpleListWalker([]))
title = urwid.Text("Transcribed")
# How do I put a scrollbar on the results box?
results = urwid.Text("")
# copy pasted from examples, just pile them on top of each other
pile = urwid.Pile([speak, div, language, div, sound_source, div, title, results])
# fill the screen
top = urwid.Filler(pile, valign="top")

urwid.MainLoop(top, palette).run()
