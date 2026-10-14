try:
    import numpy as np
    import errors
    import threading
    import soundfile as sf
    import sounddevice as sd
except Exception as e:
    errors.error(f"Error {e}")

global_lock = threading.Lock()


def test_single(device_id, filepath="testing_file/file.mp3", blocksize=1024):

    try:
        data, fs = sf.read(filepath, dtype='float32')
    except Exception as e:
        errors.error(f"Couldn't read file {filepath} with error: {e}, Does the file exist and contain audio?")

    if data.ndim == 1:
        channels = 1
        data = data.reshape(-1, 1)
    else:
        channels = int(data.shape[1])

    data = np.ascontiguousarray(data, dtype=np.float32)

    try:
        with global_lock:
            stream = sd.OutputStream(samplerate=int(fs), device=device_id, channels=channels, dtype='float32', blocksize=int(blocksize))
            stream.start()

        try:
            total_samples = len(data)
            for i in range(0, len(data), blocksize):
                chunk = data[i:i + blocksize]
                chunk_len = len(chunk)

                if chunk_len < blocksize:
                    pad_len = int(blocksize - chunk_len)
                    padding = np.zeros((pad_len, channels), dtype=np.float32)
                    chunk = np.vstack((chunk, padding))

                stream.write(np.ascontiguousarray(chunk))
        finally:
            with global_lock:
                stream.stop()
                stream.close()

    except Exception as e:
        errors.error(f"Couldn't play file {filepath} with error: {e}")

def test_multiple(device_ids, filepath="file.mp3"):
    def _runner():
        threads = []
        for i in device_ids:
            t = threading.Thread(target=test_single, kwargs={"device_id": i, "filepath": filepath})
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
    threading.Thread(target=_runner, daemon=True).start()