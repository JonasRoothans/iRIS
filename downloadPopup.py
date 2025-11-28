import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import threading
import time

class downloadPopup:
    def __init__(self):
        self.pb = {}
        self.label = {}
        self.construct_UI()



    def add_progressbar(self,tag):
        frame = ctk.CTkFrame(self.root)
        frame.pack()
        self.label[tag] = ctk.CTkLabel(frame, text=f'{tag}:')
        self.label[tag].pack(side='top', fill='x')
        self.pb[tag] = ctk.CTkProgressBar(
            frame,
            orientation='horizontal',
            mode='determinate'
        )
        self.pb[tag].set(0)
        self.pb[tag].pack(side='top', fill='x')





    def construct_UI(self):
        self.root = ctk.CTk()
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("light")
        self.root.title("Updaten...")
        self.root.geometry("500x500")

        self.tags = ['Stemmen','Meetings','Moties','Raadsvoorstellen','Amendementen','Brieven','Vragen','Bijlages','Updates','Keywords']

        for tag in self.tags:
            print(tag)
            self.add_progressbar(tag)

        self.root.update()


    def progress(self,tag,value):
        self.pb[tag] = value
        self.label[tag].configure(text=f'{tag} {int(value*100)}%: ')

    def start_task(self, tag):
        """Sets the progress bar in indeterminate (busy) mode."""
        self.pb[tag].configure(mode='indeterminate')
        self.pb[tag].start()  # Start the busy animation
        self.label[tag].configure(text=f'{tag}: running...')

    def finish_task(self, tag):
        """Sets the progress bar to 100% when the task finishes."""
        self.pb[tag].stop()  # Stop the busy animation
        self.pb[tag].configure(mode='determinate')  # Set to determinate for 100% completion
        self.pb[tag].set(1)  # Set it to 100%
        self.label[tag].configure(text=f'{tag}: 100% complete')

if __name__=='__main__':
    p = downloadPopup()
