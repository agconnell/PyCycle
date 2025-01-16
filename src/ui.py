
from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PySide6.QtCore import Slot, Signal


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import random

COLOR_LIST = ['red', 'green']

class UI(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.xvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.yvals = []

    def plot(self, title, color_id, ylabel):
        self.yvals = []
        for i in range(0, 10):
            y = random.uniform(200, 250)
            self.yvals.append(y)

        self.fig = Figure(figsize=(1300, 300))
        self.canvas = FigureCanvas(self.fig)  
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.ax.plot(self.xvals, self.yvals, color=COLOR_LIST[color_id])
        self.ax.legend().set_draggable(True)  

        self.ax.set_ylabel(ylabel, rotation='horizontal' )
        self.ax.set_title(title)
        return self.canvas

    def render(self):
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.plot("Heart Rate", 0, "BPM"))
        self.layout.addWidget(self.plot("Power", 1, "Watts"))
        self.parent.statusBar().showMessage('Ready')
        