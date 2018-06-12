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
import time
import os
import signal
import threading
from messagecontroller import displayDialogBox

current_temp = 0
new_fan_speed = 0
pause_loop = False

class Curve():

	def __init__(self, *args, **kwargs):
		if len(args) == 1: #[[temp0, speed0], [temp1, speed1], [temp2, speed2]]
			self.cpa = list(args[0])
		if len(args) == 2: #[[temp0, temp1, temp2], [speed0, speed1, speed2]]
			self.convertIntoMatrix(args[0], args[1])

	def convertIntoMatrix(self, x_values, y_values):
		self.cpa = list()
		x_temp = list(x_values)
		y_speed = list(y_values)
		for index in range(0, len(x_temp)):
			self.cpa.append([x_temp[index], y_speed[index]])

	def evaluate(self, x):
		point_i = 0
		while(point_i < len(self.cpa) - 1):

			if(self.cpa[point_i][0] <= x and self.cpa[point_i + 1][0] > x):
				point_1 = self.cpa[point_i]
				point_2 = self.cpa[point_i + 1]
				delta_x = point_2[0] - point_1[0]
				delta_y = point_2[1] - point_1[1]

				gradient = float(delta_y)/float(delta_x)

				x_bit = x - point_1[0]
				y_bit = int(float(x_bit) * gradient)
				y = point_1[1] + y_bit
				return y

			point_i += 1

	def setCurve(self, *args, **kwargs):
		if len(args) == 1:
			self.cpa = list(args[0])
		if len(args) == 2:
			self.convertIntoMatrix(args[0], args[1])


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self.stop_thread = threading.Event()

    def stop(self):
        self.stop_thread.set()

    def stopped(self):
        return self.stop_thread.isSet()

class NvidiaFanController(StoppableThread):

	DRIVER_VERSION_CHANGE = 352.09 #from this version on, we need to use a different method to change fan speed
	DRIVER_VERSIONS_ERROR = [349.16, 349.12] #cannot control fan speed in these driver versions

	"""Room here for arguments to implement multigpu fan control"""
	def __init__(self, *args, **kwargs):
		super(NvidiaFanController, self).__init__()
		signal.signal(signal.SIGINT, self.exit_signal_handler) #CTRL-C
		signal.signal(signal.SIGQUIT, self.exit_signal_handler) #CTRL-\
		signal.signal(signal.SIGHUP, self.exit_signal_handler) #terminal closed
		signal.signal(signal.SIGTERM, self.exit_signal_handler)
		self.curve_lock = threading.Lock()

		if len(args) == 1: #[[temp0, speed0], [temp1, speed1], [temp2, speed2]]
			self.curve = Curve(args[0])
		if len(args) == 2: #[[temp0, temp1, temp2], [speed0, speed1, speed2]]
			self.curve = Curve(args[0], args[1])

	def exit_signal_handler(self, signal, frame):
		self.stop_thread()

	def stop(self):
		super(NvidiaFanController, self).stop() #StoppableThread.stop()

	def run(self):
		global new_fan_speed
		global current_temp

		while(not self.stopped()):
			if (pause_loop): 
				continue # allow loop to continue running but not execute any functions
			else:
				self.curve_lock.acquire() # get Curve

				current_temp = self.getTemp()
				new_fan_speed = self.curve.evaluate(current_temp)
				# os.system("clear")
				# print("CurrTemp: {0} FanSpeed: {1}".format(current_temp,new_fan_speed))
				self.setFanSpeed(new_fan_speed)

				time.sleep(1.0)

				self.curve_lock.release()

		self.resetFan()

		# print "Exit"
		#finished and ready to exit
		return

	def resetFan(self):
		# print "Reset to Auto Fan"
		process = Popen("nvidia-settings -a [gpu:0]/GPUFanControlState=0", shell=True, stdin=PIPE, stdout=PIPE)

	def getTemp(self):
		process = Popen("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader", shell=True, stdin=PIPE, stdout=PIPE)
		new_temp = process.stdout.readlines()
		return int(new_temp[0])

	def getFanSpeed(self):
		return new_fan_speed

	def setFanSpeed(self, speed):
		drv_ver = self.getDriverVersion()

		if drv_ver >= NvidiaFanController.DRIVER_VERSION_CHANGE:
			process = Popen("nvidia-settings -a [gpu:0]/GPUFanControlState=1 -a [fan:0]/GPUTargetFanSpeed={0}".format(speed), shell=True, stdin=PIPE, stdout=PIPE)
		elif drv_ver in NvidiaFanController.DRIVER_VERSIONS_ERROR:
			displayDialogBox("Cannot control fan speed in driver version {0}. Please update your driver to use this app.".format(drv_ver))
			self.stop()
		else:
			process = Popen("nvidia-settings -a [gpu:0]/GPUFanControlState=1 -a [fan:0]/GPUCurrentFanSpeed={0}".format(speed), shell=True, stdin=PIPE, stdout=PIPE)

	def getDriverVersion(self):
		try:
			drv_ver = check_output("nvidia-smi | sed -n -e 's/^.*Version: //p' | head -c 6", shell=True)
			return drv_ver
		except Exception:
			print "Exception in parsing Nvidia Driver Version. We'll use old attribute 'GPUCurrentFanSpeed'"
			return -1

	def setCurve(self, *args, **kwargs):
		self.curve_lock.acquire()
		# print "Fan Speed Curve updated"

		if len(args) == 1:
			self.curve.setCurve(args[0])

		if len(args) == 2:
			self.curve.setCurve(args[0], args[1])

		self.curve_lock.release()


def pause(bool):
	global pause_loop
	pause_loop = bool

if __name__ == "__main__":
	print "Please launch nvda-contrl.py"

