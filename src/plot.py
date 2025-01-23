import matplotlib.pyplot as pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer
import numpy as np

from src.observer import Observer

NUMBER_OF_POINTS = 20

class Plot(QWidget, Observer):

    def __init__(self, name, ylabel, range, color, avg_color):
        super(Plot, self).__init__()

        self.timer = None
        # Create figure and axes
        self.name = name
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

    def to_time(self, secs):
        h = 0
        m = 0
        s = 0
        if secs > 3599:
            h = int(secs / 3600)
            secs = secs - h * 3600
        if secs > 59:
            m = int(secs / 60)
            secs = secs - (m * 60)    
        s = secs

        if h == 0:
            return f"{m:02}:{s:02}"
        else:
            return f"{h:02}:{m:02}:{s:02}"
    

    def update(self):
        if not self.running:
            return
        
        if len(self.yvals) > NUMBER_OF_POINTS:
            self.yvals.pop(0)
            self.xvals.pop(0)

        # Clear the previous plot
        self.ax.clear()

        # Plot the new data
        self.ax.set_ylim(0, 300)
        
        if len(self.xvals) == NUMBER_OF_POINTS:
            x = self.xvals[0::2]
            y = self.yvals[0::2]
        else:
            x = self.xvals
            y = self.yvals

        

        #add a average line first so the main line is on top
        if len(x) > 5:
            ay = [np.average(y)] * len(x)
            self.ax.plot(x, ay, color=self.avg_color, linewidth=2)

        self.ax.plot(x, y, color=self.color, linewidth=4)
        self.ax.set_ylabel(self.ylabel, labelpad=10 )
        self.ax.set_title(self.name)

        self.canvas.draw()

    def start(self):
        self.running = True
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start(1000)  # Update the label every 1000 milliseconds (1 second)

    def stop(self):
        self.running = False

    def pause(self):
        self.running = False

    def plot(self):

        self.fig = Figure(figsize=(1300, 300))
        self.canvas = FigureCanvas(self.fig)  
        self.ax = self.fig.add_subplot(1, 1, 1)

        # self.ax.plot(self.xvals, self.yvals, color=self.color)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.name)

        return self.canvas
