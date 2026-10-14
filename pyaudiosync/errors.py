try:
    import customtkinter
except Exception as e:
    print(e)

def error(msg = "Error: Null"):
    try:
        root = customtkinter.CTk()
        root.geometry("900x200")
        root.title("Error")

        label = customtkinter.CTkLabel(root, text="PyAudioSync Error")
        label.pack()

        text = customtkinter.CTkTextbox(root, width=900, height=200)
        text.insert(customtkinter.END, msg)
        text.pack()

        root.mainloop()
    except Exception as e:
        print(f"Could not create error message gui: {e}")