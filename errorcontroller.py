import Tkinter as tk
import tkMessageBox

def displayErrorBox(message):
	root = tk.Tk()
	root.withdraw()
	tkMessageBox.showerror('Error', message)
	root.destroy()

	