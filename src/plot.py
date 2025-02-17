
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer
import numpy as np
import threading

class Plot(QWidget):

    def __init__(self,name, data_field, ylabel, range, color, avg_color, callback=None):
        super(Plot, self).__init__()

        self.timer = None
        self.callback = callback
        self.workout = None

        # Create figure and axes
        self.name = name
        self.data_field = data_field
        self.ylabel = ylabel
        self.color = color
        self.avg_color = avg_color

        self.running = False
        self.yvals = [0]
        self.xvals = [0]
        self.range = range
        self.run_time = 0
        self.avg = 0

    def notify(self, data):
        self.yvals.append(data.value)
        self.xvals.append(self.to_time(data.run_time))

    def update(self):
        if not self.running:
            return
        if self.workout is None:
            return
        if self.workout.is_paused():
            return
        
        self.xvals, self.yvals, ticks = self.workout.get_data(self.data_field)
        if len(self.xvals) == 0:
            return
       
        if self.callback:
            self.callback(self.yvals[-1])

        # Clear the previous plot
        self.ax.clear()

        # Plot the new data
        self.ax.set_ylim(0, 250)   

        #add a average line first so the main line is on top
        if len(self.xvals) > 20:
            ay = [np.average(self.yvals)] * len(self.xvals)
            self.ax.plot(self.xvals, ay, color=self.avg_color, linewidth=2)

        self.ax.plot(self.xvals, self.yvals, color=self.color, linewidth=4)
        self.ax.set_xticks(ticks, minor=False)
        self.ax.set_ylabel(self.ylabel, labelpad=10 )
        self.ax.set_title(self.name)

        self.canvas.draw()

    def start(self, workout):
        self.running = True
        self.workout = workout
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start(200)  # Update the label every 1000 milliseconds (1 second)
        # t = threading.Thread(target=self.listen).start()
        # t.join()

    def stop(self):
        self.running = False

    def pause(self):
        self.paused = True

    def plot(self):

        self.fig = Figure(figsize=(1300, 300))
        self.canvas = FigureCanvas(self.fig)  
        self.ax = self.fig.add_subplot(1, 1, 1)

        # self.ax.plot(self.xvals, self.yvals, color=self.color)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.name)

        return self.canvas
