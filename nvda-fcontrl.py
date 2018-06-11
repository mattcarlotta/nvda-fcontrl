#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced version of the script made by Luke Frisken. It adds a frontend to the script,
with a drag and drop chart. The drag and drop code is a modified version of the
Drag n Drop Text Example from SciPy
Copyright (C) 2014  Claudio Pupparo

Script to control the fan speed of an NVidia gpu using a custom fan speed/temperature curve.
Copyright (C) 2012  Luke Frisken

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses.
"""
from subprocess import *
import numpy as np
import pygtk
pygtk.require('2.0')
import gtk
import Tkinter as tk
import tkMessageBox
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib.animation as animation
from datacontroller import *
from draghandler import *
import math
import signal
import time
import nvfanspeed
import pynotify
from os import path
import csv

x_values = []
y_values = []

fig = plt.figure(num="Nvidia Fan Speed Controller") #create a figure (one figure per window)
axes = fig.add_subplot(111) #add a subplot to the figure. axes is of type Axes which contains most of the figure elements
axes.set_title("Fan Speed Curve") # title for the chart

class Chart(object):
	def __init__(self, plt):
		global current_temp
		global current_fan_speed

		self.plot = plt
		self.fig = fig #create a figure (one figure per window)
		self.axes = axes #add a subplot to the figure. axes is of type Axes which contains most of the figure elements

		#working on the Axes object
		self.axes.set_title("Fan Speed Curve")
		self.axes.grid()

		self.x_min = -5
		self.x_max = 115
		self.y_min = 25
		self.y_max = 105

		self.axes.set_xlim(self.x_min, self.x_max)
		self.axes.set_ylim(self.y_min, self.y_max)

		saveFig = self.fig.add_axes([0.8, 0.02, 0.1, 0.04])
		self.saveFig = Button(saveFig, "Save")
		self.saveFig.on_clicked(self.saveToFile)

		# printAxes = self.fig.add_axes([0.2, 0.025, 0.1, 0.04])  #position rect [left, bottom, width, height] where all quantities are in fractions of figure width and height
		# self.printButton = Button(printAxes, "Print")
		# self.printButton.on_clicked(self.printData)

		applyAxes = self.fig.add_axes([0.685, 0.02, 0.1, 0.04])
		self.applyAxes = Button(applyAxes, "Apply")
		self.applyAxes.on_clicked(self.applyData)

		#b=blue, o=circle, picker=max distance for considering point as clicked
		self.line, = axes.plot(x_values, y_values, linestyle='-', marker='o', color='b', picker=5) #tuple unpacking: this function returns a tuple, with the comma we take the first element

		self.dragHandler = DragHandler(self)
		self.dataController = DataController(x_values, y_values)

		#validate points from file!
		self.nvidiaController = nvfanspeed.NvidiaFanController(x_values, y_values)
		self.nvidiaController.start()

		signal.signal(signal.SIGINT, self.exit_signal_handler) #CTRL-C
		signal.signal(signal.SIGQUIT, self.exit_signal_handler) #CTRL-\
		signal.signal(signal.SIGHUP, self.exit_signal_handler) #terminal closed
		signal.signal(signal.SIGTERM, self.exit_signal_handler)

		self.fig.canvas.mpl_connect("close_event", self.on_close)
		# self.updateLabelStats(axes)

	def on_close(self, event):
		self.nvidiaController.stop()

	def exit_signal_handler(self, signal, frame):
		self.close()

	def close(self):
		self.plot.close('all')
		self.nvidiaController.stop()

	def show(self):
		self.plot.show() #display ALL non closed figures
		#pyplot is stateful: usually self.plot.function() works on the current plot in the current figure

	# def printData(self, event):
	# 	xdata, ydata = self.dataController.getData()
	# 	print "---------------"
	# 	for index in range(0, len(xdata)):
	# 		print xdata[index], ydata[index]
	# 	print "---------------"

	def applyData(self, event):
		xdata = self.line.get_xdata()
		ydata = self.line.get_ydata()
		ret = self.dataController.setData(xdata, ydata)

		if ret:
			self.nvidiaController.setCurve(xdata, ydata)
			sendMessage('Successfully applied curve to fan settings!')
		else:
			xdata, ydata = self.dataController.getData()
			xydata = [xdata, ydata]
			self.line.set_data(xydata)

	def saveToFile(self, event):
		config = []
		xdata, ydata = self.dataController.getData()
		for index in range(0, len(xdata)):
			res = [xdata[index], ydata[index]]
			config.append(res)
		savedConfig = np.array(config)
		np.savetxt("config.csv", savedConfig.astype(int) , delimiter=",", fmt='%i')
		sendMessage('Successfully saved curve config!')

def sendMessage(message):
	root = tk.Tk()
	root.withdraw()
	tkMessageBox.showinfo('Message', message)
	root.destroy()

def updateLabelStats(i):
	current_temp = nvfanspeed.NvidiaFanController().getTemp()
	axes.set_xlabel("Temperature "+ "(" + str(current_temp) +"°C)")
	current_fan_speed = str(nvfanspeed.NvidiaFanController().getFanSpeed())
	axes.set_ylabel("Fan Speed " + "(" + str(current_fan_speed) + "%)")

def initChartValues():
	global x_values
	global y_values

	if path.exists("config.csv"):
		with open('config.csv', 'r') as csvfile:
			config = csv.reader(csvfile, delimiter=',')
			for row in config:
				x_values.append(int(row[0]))
				y_values.append(int(row[1]))

	x_values = x_values or [0,  10, 20, 30, 40, 50, 60, 65, 70, 80, 90, 100] #temp
	y_values = y_values or [30, 35, 40, 45, 55, 60, 65, 70, 75, 85, 95, 100] #speed

if __name__ == "__main__":
	ani = animation.FuncAnimation(fig, updateLabelStats, interval=1000)
	initChartValues()
	chart = Chart(plt)
	chart.show()
	plt.show()
