import os
import re
import threading
import time

from kivy.utils import platform

import errors

# Absolute path so it works regardless of the working directory
TEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testing_file", "file.mp3")


class Backend:
    """Interface: list_devices(), play(), test(), stop_all()."""

    def __init__(self):
        self._lock = threading.Lock()
        self._events = set()

    def _new_event(self):
        ev = threading.Event()
        with self._lock:
            self._events.add(ev)
        return ev

    def _release(self, ev):
        with self._lock:
            self._events.discard(ev)

    def stop_all(self):
        with self._lock:
            for ev in self._events:
                ev.set()

    def test(self, device_ids):
        self.play(device_ids, TEST_FILE)

    def list_devices(self):
        return []

    def play(self, device_ids, filepath):
        pass


class NullBackend(Backend):
    """Used when audio can't be initialised, so the UI still opens."""


# --------------------------------------------------------------------------
# Desktop: sounddevice + soundfile
# --------------------------------------------------------------------------
class DesktopBackend(Backend):
    BLOCKSIZE = 1024

    def __init__(self):
        super().__init__()
        import numpy as np
        import sounddevice as sd
        import soundfile as sf

        self.np, self.sd, self.sf = np, sd, sf
        self._stream_lock = threading.Lock()

    def list_devices(self):
        try:
            result, seen = [], set()
            for i, dev in enumerate(self.sd.query_devices()):
                if dev["max_output_channels"] <= 0:
                    continue
                clean = dev["name"].split(" (@")[0]
                norm = re.sub(r"\s*\(.*?\)", "", clean)
                norm = re.sub(r"\s+\d+$", "", norm).strip().lower()
                if norm in seen:
                    continue
                seen.add(norm)
                result.append({"id": i, "name": clean})
            if not result:
                errors.error("No audio output devices found.")
            return result
        except Exception as e:
            errors.error(f"Unable to get list of audio devices: {e}")
            return []

    def play(self, device_ids, filepath):
        stop = self._new_event()

        def runner():
            try:
                threads = [
                    threading.Thread(target=self._play_single, args=(d, filepath, stop))
                    for d in device_ids
                ]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            finally:
                self._release(stop)

        threading.Thread(target=runner, daemon=True).start()

    def _play_single(self, device_id, filepath, stop):
        np, sd, sf = self.np, self.sd, self.sf
        bs = self.BLOCKSIZE
        try:
            data, fs = sf.read(filepath, dtype="float32", always_2d=True)
        except Exception as e:
            errors.error(f"Couldn't read file {filepath}: {e}. Does the file exist and contain audio?")
            return

        channels = data.shape[1]
        data = np.ascontiguousarray(data)

        try:
            with self._stream_lock:
                stream = sd.OutputStream(samplerate=int(fs), device=device_id,
                                         channels=channels, dtype="float32", blocksize=bs)
                stream.start()
            try:
                for i in range(0, len(data), bs):
                    if stop.is_set():
                        break
                    chunk = data[i:i + bs]
                    if len(chunk) < bs:
                        pad = np.zeros((bs - len(chunk), channels), dtype=np.float32)
                        chunk = np.vstack((chunk, pad))
                    stream.write(np.ascontiguousarray(chunk))
            finally:
                with self._stream_lock:
                    stream.stop()
                    stream.close()
        except Exception as e:
            errors.error(f"Couldn't play file {filepath}: {e}")


# --------------------------------------------------------------------------
# Android: MediaPlayer + AudioManager through pyjnius
# --------------------------------------------------------------------------
class AndroidBackend(Backend):
    TYPE_NAMES = {
        1: "Earpiece", 2: "Speaker", 3: "Wired headset", 4: "Wired headphones",
        7: "Bluetooth (call)", 8: "Bluetooth", 9: "HDMI", 11: "USB device",
        22: "USB headset",
    }

    def __init__(self):
        super().__init__()
        from jnius import autoclass, cast

        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        Context = autoclass("android.content.Context")
        self._AudioManager = autoclass("android.media.AudioManager")
        self._MediaPlayer = autoclass("android.media.MediaPlayer")
        self._am = cast("android.media.AudioManager",
                        activity.getSystemService(Context.AUDIO_SERVICE))
        self._devices = {}  # id -> AudioDeviceInfo

    def list_devices(self):
        try:
            infos = self._am.getDevices(self._AudioManager.GET_DEVICES_OUTPUTS)
            result = []
            self._devices = {}
            for d in infos:
                if not d.isSink():
                    continue
                dev_id = d.getId()
                self._devices[dev_id] = d
                label = self.TYPE_NAMES.get(d.getType(), f"Type {d.getType()}")
                result.append({"id": dev_id, "name": f"{label} - {d.getProductName()}"})
            if not result:
                errors.error("No audio output devices found.")
            return result
        except Exception as e:
            errors.error(f"Unable to get list of audio devices: {e}")
            return []

    def play(self, device_ids, filepath):
        stop = self._new_event()
        threading.Thread(target=self._run, args=(list(device_ids), filepath, stop),
                         daemon=True).start()

    def _run(self, device_ids, filepath, stop):
        players = []
        try:
            # Prepare everything first, then start all players back to back
            for dev_id in device_ids:
                mp = self._MediaPlayer()
                players.append(mp)
                mp.setDataSource(filepath)
                if not mp.setPreferredDevice(self._devices[dev_id]):
                    raise RuntimeError(f"Android refused to route audio to device {dev_id}")
                mp.prepare()

            if not stop.is_set():
                for mp in players:
                    mp.start()

            while not stop.is_set() and any(mp.isPlaying() for mp in players):
                time.sleep(0.05)
        except Exception as e:
            errors.error(f"Couldn't play file {filepath}: {e}")
        finally:
            for mp in players:
                try:
                    mp.stop()
                except Exception:
                    pass
                try:
                    mp.release()
                except Exception:
                    pass
            self._release(stop)


def get_backend():
    try:
        return AndroidBackend() if platform == "android" else DesktopBackend()
    except Exception as e:
        errors.error(f"Could not initialise audio: {e}")
        return NullBackend()