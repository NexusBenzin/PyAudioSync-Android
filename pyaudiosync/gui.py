import os

try:
    import errors
    import test
    import play_file as pf
    import playback_control
except Exception as e:
    print(e)

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup

AUDIO_FILTERS = ["*.mp3", "*.wav", "*.ogg", "*.aac", "*.flac", "*.alac", "*.aiff"]


class DeviceRow(BoxLayout):
    text = StringProperty("")

    def __init__(self, device_id, text, on_toggle, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.ids.cb.bind(active=lambda cb, active: on_toggle(device_id, active))


class MainView(BoxLayout):
    quote = StringProperty("")


class PyAudioSyncApp(App):
    title = "PyAudioSync"

    def on_start(self):
        errors.flush_pending()

    def __init__(self, device_list, quote, **kwargs):
        super().__init__(**kwargs)
        self.device_list = device_list
        self.quote = quote
        self.selected_devices = set()
        self.file = None

    def build(self):
        try:
            root = MainView(quote=self.quote)
            container = root.ids.device_list
            for device in self.device_list:
                container.add_widget(
                    DeviceRow(
                        device_id=device["id"],
                        text=f"ID {device['id']}: {device['name']}",
                        on_toggle=self.toggle_device,
                    )
                )
            return root
        except Exception as e:
            errors.error(f"Could not create main GUI: {e}")

    def toggle_device(self, device_id, active):
        try:
            if active:
                self.selected_devices.add(device_id)
            else:
                self.selected_devices.discard(device_id)
        except Exception as e:
            errors.error(f"Could not toggle device: {e}")

    def test_selected(self):
        if self.selected_devices:
            test.test_multiple(list(self.selected_devices))
        else:
            print("No device selected")

    def play_selected(self):
        if not self.selected_devices:
            errors.error("No device selected")
        elif not self.file:
            errors.error("No file selected")
        else:
            pf.play_file_multiple(list(self.selected_devices), self.file)

    def select_file(self):
        chooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=AUDIO_FILTERS,
        )
        ok = Button(text="Select", size_hint_y=None, height=48)
        content = BoxLayout(orientation="vertical")
        content.add_widget(chooser)
        content.add_widget(ok)

        popup = Popup(title="Select file", content=content, size_hint=(0.9, 0.9))

        def confirm(*_):
            try:
                if not chooser.selection:
                    errors.error("No file selected")
                    return
                self.file = chooser.selection[0]
                popup.dismiss()
            except Exception as e:
                errors.error(f"Could not open file: {chooser.selection} error: {e}")

        ok.bind(on_release=confirm)
        popup.open()

        def stop_playing(self):
            playback_control.stop_all()

def gui(device_list, quote):
    PyAudioSyncApp(device_list, quote).run()