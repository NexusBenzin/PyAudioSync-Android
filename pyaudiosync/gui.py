try:
    import errors
    import customtkinter
    import test
    import play_file as pf
    from tkinter import filedialog
except Exception as e:
    print(e)

file = None


def gui(device_list, quote):

    def select_file():
        global file
        try:
            path = filedialog.askopenfilename(title="Select file", filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.aac *.flac *.alac *.aiff")])
            if not path:
                errors.error("No file selected")
            file = path
        except Exception as e:
            errors.error(f"Could not open file: {path} error: {e}")


    selected_devices = set()

    try:
        root = customtkinter.CTk()
        root.title("PyAudioSync")
        root.geometry("1920x1080")

        Label = customtkinter.CTkLabel(root, text=quote)
        Label.pack()

        listbox = customtkinter.CTkScrollableFrame(root, width=600, height=600)
        listbox.pack()
    except Exception as e:
        errors.error(f"Could not create main GUI: {e}")

    def toggle_device(device_id):
        try:
            if device_id in selected_devices:
                selected_devices.remove(device_id)
            else:
                selected_devices.add(device_id)
        except Exception as e:
            errors.error(f"Could not toggle device: {e}")
    try:
        for device in device_list:
            row_frame = customtkinter.CTkFrame(listbox, fg_color="transparent")
            row_frame.pack(fill="x", pady=5, padx=5 )



            cb = customtkinter.CTkCheckBox(row_frame, text="", width=24, command=lambda d_id=device['id']: toggle_device(d_id))
            cb.pack(side="left", anchor="n")


            label = customtkinter.CTkLabel(row_frame, text=f"ID {device['id']}: {device['name']}", wraplength=350, justify="left")
            label.pack(side="left", padx=5, fill="x")

        btn_test = customtkinter.CTkButton(root, text="Test selected", command=lambda: test.test_multiple(list(selected_devices)) if selected_devices else print("No device selected"))
        btn_test.pack()

        btn_play = customtkinter.CTkButton(root, text="Play file on selected", command=lambda: pf.play_file_multiple(list(selected_devices), file) if selected_devices else errors.error("No device selected"))
        btn_play.pack(pady=5)

        btn_select_file = customtkinter.CTkButton(root, text="Select file", command=lambda: select_file())
        btn_select_file.pack(pady=0)
    except Exception as e:
        errors.error(e)

    root.mainloop()
