
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QFont, QPalette, QColor
from src.plot import Plot

from src.workout import Workout

class UI(QWidget):
    lbl_font = QFont("Arial", 16, QFont.Bold)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.start_btn = QPushButton("Start")
        self.pause_btn = None
        self.stop_btn = None
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.hr_lbl = QLabel("--")
        self.hr_lbl.setFont(self.lbl_font)
        palette = self.hr_lbl.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
        self.hr_lbl.setPalette(palette)
        self.start_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.stop_btn.clicked.connect(self.stop)
        self.workout = None

    def start(self):
        self.parent.statusBar().showMessage('Started')
        self.workout = Workout()
        self.workout.start()
        self.hr.start(self.workout)
        self.power.start(self.workout)
        self.cadence.start(self.workout)

    def pause(self):
        self.parent.statusBar().showMessage('Paused')
        self.workout.pause()
        self.hr.pause()
        self.power.pause()
        self.cadence.pause()
        
    def stop(self):
        self.parent.statusBar().showMessage('Stopped')
        self.workout.stop()
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
        hrm_layout = QHBoxLayout(self)
        self.layout.addLayout(hrm_layout)
        self.hr = Plot("Heart Rate","BPM", (60, 150), 'red', 'lightcoral', self.set_hr_label, port=1234)
        hrm_layout.addWidget(self.hr.plot())
        hrm_layout.addWidget(self.hr_lbl)

        self.power = Plot("Power", "Watts", (200, 250), "green", 'palegreen', port=1235)
        self.layout.addWidget(self.power.plot())

        self.cadence = Plot("Cadence", "RPM", (70, 120), "blue", 'lightskyblue', port=1236)
        self.layout.addWidget(self.cadence.plot())

    def set_hr_label(self, value):
        self.hr_lbl.setText(f"{value} bpm")

    def render(self):
        self.layout = QVBoxLayout(self)
        self.render_buttons()
        self.render_plots()

        self.parent.statusBar().showMessage('Ready')

        