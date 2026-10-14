import sys

from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

_pending = []


def error(msg="Error: Null"):
    msg = str(msg)
    print(f"PyAudioSync Error: {msg}", file=sys.stderr)
    if App.get_running_app() is not None:
        _show_popup(msg)
    else:
        _pending.append(msg)


def flush_pending():
    if _pending:
        msg = "\n\n".join(_pending)
        _pending.clear()
        _show_popup(msg)


@mainthread
def _show_popup(msg):
    try:
        label = Label(text=msg, halign="left", valign="top")
        label.bind(size=lambda inst, size: setattr(inst, "text_size", size))

        close = Button(text="Close", size_hint_y=None, height=48)
        content = BoxLayout(orientation="vertical", spacing=10)
        content.add_widget(label)
        content.add_widget(close)

        popup = Popup(title="PyAudioSync Error", content=content, size_hint=(0.8, 0.5))
        close.bind(on_release=popup.dismiss)
        popup.open()
    except Exception as e:
        print(f"Could not create error message gui: {e} ")