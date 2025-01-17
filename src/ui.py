
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from src.plot import Plot

COLOR_LIST = ['red', 'green']

class UI(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.start_btn = QPushButton("Start")
        self.pause_btn = None
        self.stop_btn = None
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.start_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.stop_btn.clicked.connect(self.stop)

    def start(self):
        self.parent.statusBar().showMessage('Started')
        self.hr.start()
        self.power.start()
        self.cadence.start()

    def pause(self):
        self.parent.statusBar().showMessage('Paused')
        self.hr.pause()
        self.power.pause()
        self.cadence.pause()
        
    def stop(self):
        self.parent.statusBar().showMessage('Stopped')
        self.hr.stop()
        self.power.stop()
        self.cadence.stop()
        

    def render_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)
        self.layout.addLayout(button_layout)

    def render_plots(self):

        self.hr = Plot("Heart Rate","BPM", (60, 150), 'red', 'lightcoral')
        self.layout.addWidget(self.hr.plot())

        self.power = Plot("Power", "Watts", (200, 250), "green", 'palegreen')
        self.layout.addWidget(self.power.plot())

        self.cadence = Plot("Cadence", "RPM", (70, 120), "blue", 'lightskyblue')
        self.layout.addWidget(self.cadence.plot())

    def render(self):
        self.layout = QVBoxLayout(self)
        self.render_buttons()
        self.render_plots()

        self.parent.statusBar().showMessage('Ready')

        