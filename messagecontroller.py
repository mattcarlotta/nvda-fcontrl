import Tkinter as tk
import tkMessageBox

def displayDialogBox(message):
	root = tk.Tk()
	root.withdraw()
	tkMessageBox.showinfo('Message', message)
	root.destroy()