import os

import errors
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.utils import platform

AUDIO_FILTERS = ["*.mp3", "*.wav", "*.ogg", "*.aac", "*.flac", "*.aiff"]


# 1. Defined MainView so Kivy and Python recognize it
class MainView(BoxLayout):
    pass

class DeviceRow(BoxLayout):
    text = StringProperty("")

    def __init__(self, device_id, text, on_toggle, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.ids.cb.bind(active=lambda cb, active: on_toggle(device_id, active))


class PyAudioSyncApp(App):
    title = "PyAudioSync"

    def __init__(self, device_list, backend, **kwargs):
        super().__init__(**kwargs)
        self.device_list = device_list or []
        self.backend = backend
        self.selected_devices = set()
        self.file = None

    def build(self):
        try:
            # Instantiated MainView correctly
            root = MainView()
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

    def on_start(self):
        errors.flush_pending()
        if platform == "android":
            try:
                from android.permissions import request_permissions
                request_permissions([
                    "android.permission.READ_EXTERNAL_STORAGE",
                    "android.permission.READ_MEDIA_AUDIO",
                ])
            except Exception as e:
                errors.error(f"Could not request storage permission: {e}")

    def on_stop(self):
        self.backend.stop_all()

    def toggle_device(self, device_id, active):
        if active:
            self.selected_devices.add(device_id)
        else:
            self.selected_devices.discard(device_id)

    def test_selected(self):
        if self.selected_devices:
            self.backend.test(list(self.selected_devices))
        else:
            errors.error("No device selected")

    def play_selected(self):
        if not self.selected_devices:
            errors.error("No device selected")
        elif not self.file:
            errors.error("No file selected")
        else:
            self.backend.play(list(self.selected_devices), self.file)

    def stop_playing(self):
        self.backend.stop_all()

    def _start_path(self):
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path
                return primary_external_storage_path()
            except Exception:
                pass
        return os.path.expanduser("~")

    def select_file(self):
        chooser = FileChooserListView(path=self._start_path(), filters=AUDIO_FILTERS)
        ok = Button(text="Select", size_hint_y=None, height=48)
        content = BoxLayout(orientation="vertical")
        content.add_widget(chooser)
        content.add_widget(ok)
        popup = Popup(title="Select file", content=content, size_hint=(0.9, 0.9))

        def confirm(*_):
            if not chooser.selection:
                errors.error("No file selected")
                return
            self.file = chooser.selection[0]
            popup.dismiss()

        ok.bind(on_release=confirm)
        popup.open()


def gui(device_list, backend):
    PyAudioSyncApp(device_list, backend).run()