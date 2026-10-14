try:
    from devices import AudioDeviceManager
    from gui import gui
    from quote import get_quote
    import errors
except Exception as e:
    print(e)

try:
    devices = AudioDeviceManager.get_devices()

    quote_data = get_quote()
    gui(device_list=devices, quote=(f"{quote_data['quote']} - {quote_data['author']}"))

except Exception as e:
    errors.error(f"Could not start application: {e}")




  