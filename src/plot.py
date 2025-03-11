
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget

MAX_POINTS = 100
TICK_GAP = 30 #30 seconds
XAXIS_RANGE = 60*5 #5 minutes

class Plot(QWidget):
    '''Plots values from an LRU'''
    def __init__(self,name, data_field, ylabel, yrange, color, avg_color, callback=None):
        super(Plot, self).__init__()

        self.timer = None
        self.callback = callback
        self.workout = None

        # setup plot options
        self.name = name
        self.data_field = data_field
        self.ylabel = ylabel
        self.color = color
        self.avg_color = avg_color

        # setup the actual plot
        self.fig = Figure(figsize=(1300, 300))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.line = Line2D([], [], color=self.color, linewidth=5)

        # state variables
        self.running = False
        self.yvals = [0]
        self.xvals = [0]
        self.yrange = yrange
        self.run_time = 0
        self.avg = 0

    def ticker(self, Xmin, Xmax, num_points):
        '''Creates nicely spaced ticks for the xAxis
        not currently used and maybe not needed'''
        ticks = []
        Xmax = Xmax + TICK_GAP
        if num_points < XAXIS_RANGE:
            Xmin = 0
            Xmax = XAXIS_RANGE + TICK_GAP
        for i in range(Xmin, Xmax, TICK_GAP):
            ticks.append(i)
        return ticks
    
    def update(self):
        '''update the plot with the latest data'''
        if not self.running:
            return
        if self.workout is None:
            return

        x, y = self.workout.get_last_point(self.data_field)
        x_data = self.line.get_xdata()
        y_data = self.line.get_ydata()
        x_data.append(x)
        y_data.append(y)

        while len(x_data) > MAX_POINTS:
            x_data.pop(0)
            y_data.pop(0)
        self.line.set_xdata(x_data)
        self.line.set_ydata(y_data)
        tks = self.ticker(x_data[0], x_data[-1], MAX_POINTS)
        self.ax.set_xticks(tks, minor=False)
        # self.ax.relim()            # Recalculate limits
        # self.ax.autoscale_view(tight=True, scalex=True, scaley=False)

        # tks = self.ticker(self.xvals[0], self.xvals[-1], MAX_POINTS)
        self.fig.tight_layout()
        self.canvas.draw()
        self.canvas.flush_events()

    def connect(self, workout):
        '''connect to LRU'''
        self.running = True
        self.workout = workout

    def start(self):
        '''Start workout'''
        self.running = True

    def stop(self):
        '''stop workout'''
        self.running = False

    def plot(self):
        '''Plot the workout '''
        self.ax.add_line(self.line)
        self.ax.set_ylim(self.yrange[0], self.yrange[1])
        # self.ax.plot(self.xvals, self.yvals, color=self.color)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.name)

        return self.canvas
