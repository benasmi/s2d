from tkinter import *
import customtkinter as ct
import os
from PIL import Image

'''
ct.set_appearance_mode("dark")

root = ct.CTk()
root.geometry('1024x640')

test = ct.CTkFrame()

upload_btn = ct.CTkButton(root, text="Upload diagram").place(relx=0.5, rely=0.5, anchor=CENTER)

root.mainloop()
'''


class ScrollableLabelButtonFrame(ct.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = ct.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, image=None):
        label = ct.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = ct.CTkButton(self, text="Command", width=100, height=24)
        if self.command is not None:
            button.configure(command=lambda: self.command(item))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return

class App(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title("S2D")
        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        left_rail = ct.CTkFrame(self, width=300, corner_radius=4)
        left_rail.columnconfigure(0)
        left_rail.rowconfigure(0)
        left_rail.rowconfigure(1, weight=1)
        left_rail.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        app_label = ct.CTkLabel(left_rail, text="History", height=30, font=("Verdana", 25))
        app_label.grid(row=0, column=1, padx=15, pady=15)

        # create scrollable label and button frame
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.scrollable_label_button_frame1 = ScrollableLabelButtonFrame(master=left_rail, width=300,
                                                                        command=self.label_button_frame_event,
                                                                         fg_color="transparent",
                                                                        corner_radius=0)
        self.scrollable_label_button_frame1.grid(row=1, column=1, padx=0, pady=0, sticky="nsew")
        for i in range(10):  # add items with images
            self.scrollable_label_button_frame1.add_item(f"image and item {i}", image=ct.CTkImage(
                Image.open(os.path.join(current_dir, "chat_light.png"))))

        upload_button = ct.CTkButton(left_rail, text="Upload", fg_color="#008000", hover_color='#004d00')
        upload_button.grid(row=2, column=1, padx=30, pady=30, sticky="nsew")

        right_rail = ct.CTkFrame(master=self, width=300, corner_radius=4)
        right_rail.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

    def label_button_frame_event(self, item):
        print(f"label button frame clicked: {item}")


if __name__ == "__main__":
    ct.set_appearance_mode("dark")
    app = App()
    app.geometry('1366x640')
    app.resizable(False, False)
    app.mainloop()
