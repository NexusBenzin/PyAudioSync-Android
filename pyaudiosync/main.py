try:
    import errors
    from audio_backend import get_backend
    from gui import gui
except Exception as e:
    print(e)

try:
    backend = get_backend()
    gui(
        device_list=backend.list_devices(),
        backend=backend,
    )
except Exception as e:
    errors.error(f"Could not start application: {e}")