from errorcontroller import displayErrorBox

class DragHandler(object):
	def __init__(self, chartObj):
		self.dragged = None
		self.chartObj = chartObj
		self.chartObj.fig.canvas.mpl_connect("pick_event", self.on_pick_event)
		self.chartObj.fig.canvas.mpl_connect("button_release_event", self.on_release_event)

	def on_pick_event(self, event):
		self.dragged = event.artist #Line2D
		self.pick_pos = (event.mouseevent.xdata, event.mouseevent.ydata)
		self.ind = event.ind

		if self.ind[0] == 0:
			# print "ERROR: cannot modify first point"
			self.dragged = None
			displayErrorBox("Can't modify the first point!")
		elif self.ind[0] == len(self.dragged.get_xdata()) - 1:
			# print "ERROR: cannot modify last point"
			self.dragged = None
			displayErrorBox("Can't modify the last point!")

		#print "self.ind: ", self.ind
		#xdata = self.dragged.get_xdata()
		#ydata = self.dragged.get_ydata()
		#print 'onpick points:', xdata[self.ind], ydata[self.ind]

	def on_release_event(self, event):
		if self.dragged is not None:
			xdata = self.dragged.get_xdata() #no need to copy the list, since it is used only by the line2D object
			ydata = self.dragged.get_ydata()
			index = self.ind #if two or more points are too closed, this tuple contains more than one point. we take the first
			chartObj = self.chartObj
			if event.xdata <= chartObj.x_min or event.xdata >= chartObj.x_max or event.ydata <= chartObj.y_min or event.ydata >= chartObj.y_max:
				# print "ERROR: cannot move point [",index[0],"] out of chart"
				displayErrorBox("Can't move point {0} off of the chart!".format(index[0]))
				return

			xdata[index[0]] = int(xdata[index[0]] + event.xdata - self.pick_pos[0]) #truncate towards zero
			ydata[index[0]] = int(ydata[index[0]] + event.ydata - self.pick_pos[1])
			#print 'new point:', xdata[index], ydata[index]

			xydata = [xdata, ydata]
			self.dragged.set_data(xydata)
			self.dragged = None
			self.chartObj.fig.canvas.draw()