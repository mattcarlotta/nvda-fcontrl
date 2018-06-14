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
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import animation, style
from datacontroller import *
from draghandler import *
from messagecontroller import displayDialogBox
import math
import signal
import time
import nvfanspeed
import os
from os import path
import csv

style.use(['seaborn-dark', 'seaborn-talk']) # current plot theme
# print style.available

x_values = []
y_values = []

fig = plt.figure(num="Nvidia Fan Controller", figsize=(12, 9)) #create a figure (one figure per window)
fig.canvas.toolbar.pack_forget()
axes = fig.add_subplot(111) #add a subplot to the figure. axes is of type Axes which contains most of the figure elements
update_stats = True # sets flag for updating chart with GPU stats


class Chart(object):
	def __init__(self, plt):
		global current_temp
		global current_fan_speed

		self.plot = plt # create instance of plt
		self.fig = fig # create a figure (one figure per window)
		self.axes = axes # add a subplot to the figure. axes is of type Axes which contains most of the figure elements

		# working on the Axes object
		self.axes.set_title("GPU Fan Controller") # title for the chart
		self.axes.grid()

		# chart min/max display values
		self.x_min = -5
		self.x_max = 105
		self.y_min = 25
		self.y_max = 105
		self.axes.set_xlim(self.x_min, self.x_max)
		self.axes.set_ylim(self.y_min, self.y_max)

		# Save button
		saveFig = self.fig.add_axes([0.8, 0.015, 0.1, 0.04])
		self.saveFig = Button(saveFig, "Save")
		self.saveFig.on_clicked(self.saveToFile)

		# printAxes = self.fig.add_axes([0.2, 0.025, 0.1, 0.04])  #position rect [left, bottom, width, height] where all quantities are in fractions of figure width and height
		# self.printButton = Button(printAxes, "Print")
		# self.printButton.on_clicked(self.printData)

		# Reset button
		resetChart = self.fig.add_axes([0.125, 0.015, 0.1, 0.04])
		self.resetChart = Button(resetChart, "Reset")
		self.resetChart.on_clicked(self.resetData)

		# Apply button
		applyAxes = self.fig.add_axes([0.685, 0.015, 0.1, 0.04])
		self.applyAxes = Button(applyAxes, "Apply")
		self.applyAxes.on_clicked(self.applyData)

		#b=blue, o=circle, picker=max distance for considering point as clicked
		self.line, = axes.plot(x_values, y_values, linestyle='-', marker='o', color='b', picker=5) #tuple unpacking: this function returns a tuple, with the comma we take the first element

		self.dragHandler = DragHandler(self)
		self.dataController = DataController(x_values, y_values)

		#validate points from file!
		self.updatedCurve = nvfanspeed.updatedCurve
		self.nvidiaController = nvfanspeed.NvidiaFanController(x_values, y_values)
		self.nvidiaController.start()

		# signal traps
		signal.signal(signal.SIGINT, self.exit_signal_handler) #CTRL-C
		signal.signal(signal.SIGQUIT, self.exit_signal_handler) #CTRL-\
		signal.signal(signal.SIGHUP, self.exit_signal_handler) #terminal closed
		signal.signal(signal.SIGTERM, self.exit_signal_handler)

		# close app
		self.fig.canvas.mpl_connect("close_event", self.on_close)

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

	def resetData(self, event):
		initChartValues() # reset to initial values
		xydata = [x_values, y_values]
		self.line.set_data(xydata) # update curve with values
		self.updateChart(x_values, y_values) # update chart to reflect values

	def updateChart(self, xdata, ydata):
		"""
		Due to how the NvidiaFanController run loop was structured to constantly update, there was an issue where updating the curve points could take anywhere from 3 to 10+ loop iterations
		By pausing the loop, updates to the curve points occur consistently between 1-3 loop iterations
		As a precaution, updating the chart with GPU temp/fan speed stats have also been paused, although may not be necessary.
		"""
		self.setUpdateStats(False) # temporarily stops live GPU updates
		self.updatedCurve(True) # pauses the nvfanspeed run loop
		self.nvidiaController.setCurve(xdata, ydata) # updates curve with new x and y data
		self.updatedCurve(False) # resumes nvfanspeed loop
		self.setUpdateStats(True) # enables live GPU updates

	def setUpdateStats(self, bool):
		global update_stats
		update_stats = bool

	def applyData(self, event):
		xdata = self.line.get_xdata() # grabs current curve y data
		ydata = self.line.get_ydata() # grabs current curve y data
		is_valid_curve = self.dataController.setData(xdata, ydata) # checks if curve is exponentially growing (returns bool)

		if is_valid_curve:
			self.updateChart(xdata, ydata) # updates nvfanspeed.NvidiaFanController() with new curve data
			displayDialogBox('Successfully applied the current curve to the fan settings!')
		else:
			xdata, ydata = self.dataController.getData() # gets previous data
			xydata = [xdata, ydata] 
			self.line.set_data(xydata) # resets line to previous curve

	def saveToFile(self, event):
		config = []
		xdata, ydata = self.dataController.getData() # get current curve points

		for index in range(0, len(xdata)):
			res = [xdata[index], ydata[index]] # combine x and y data
			config.append(res) # append it to config

		savedConfig = np.array(config) # convert config to numpy array (req'd to convert base10 to int)
		np.savetxt("config.csv", savedConfig.astype(int) , delimiter=",", fmt='%i') # saves array[temp, fspd] to config.csv
		displayDialogBox('Successfully saved the current curve configuration!')

def updateLabelStats(i):
	if (update_stats):
		current_temp = nvfanspeed.NvidiaFanController().getTemp() # grabs current temp from NvidiaFanController
		axes.set_xlabel("Temperature "+ "(" + str(current_temp) +"°C)") # updates chart x-axis label
		current_fan_speed = str(nvfanspeed.NvidiaFanController().getFanSpeed()) # grabs current fspd from NvidiaFanController
		axes.set_ylabel("Fan Speed " + "(" + str(current_fan_speed) + "%)") # updates chart y-axis label

def initChartValues():
	global x_values
	global y_values

	x_values = [0,  10, 20, 30, 40, 50, 60, 65, 70, 80, 90, 100] # default values
	y_values = [30, 35, 40, 45, 55, 60, 65, 70, 75, 85, 95, 100] # default values

	cfg_x = []
	cfg_y = []

	# Load array [temp, fspd] from csv
	if path.exists("config.csv"):
		with open('config.csv', 'r') as csvfile:
			config = csv.reader(csvfile, delimiter=',')
			for row in config:
				cfg_x.append(int(row[0]))
				cfg_y.append(int(row[1]))

		# updates default curve values with csv array
		x_values = cfg_x #temp
		y_values = cfg_y #speed

def main():
	ani = animation.FuncAnimation(fig, updateLabelStats, interval=1000) # updates the chart labels with GPU stats every 1s
	initChartValues() # attempts to initalize chart values from config.csv
	chart = Chart(plt) # builds chart fig
	chart.show() # displays chart
	

if __name__ == "__main__":
	main()

