
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
from src.plot import Plot

from src.workout import Workout

class UI(QWidget):
    lbl_font = QFont("Arial", 46, QFont.Bold)
    lbl_width = 100
    lbl_alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    btn_font = QFont("Arial", 12, QFont.Bold)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        #buttons labels and ui stuff
        self.connect_btn = QPushButton("Pair")
        self.connect_btn.setFont(self.btn_font)

        self.start_btn = QPushButton("Start")
        self.start_btn.setFont(self.btn_font)
        self.start_btn.setDisabled(True)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setFont(self.btn_font)
        self.pause_btn.setDisabled(True)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFont(self.btn_font)
        self.stop_btn.setDisabled(True)

        self.done_btn = QPushButton("Done")
        self.done_btn.setFont(self.btn_font)
        self.done_btn.setDisabled(True)

        self.hr_lbl = QLabel("--")
        self.hr_lbl.setFont(self.lbl_font)

        self.pow_lbl = QLabel("--")
        self.pow_lbl.setFont(self.lbl_font)

        self.cad_lbl = QLabel("--")
        self.cad_lbl.setFont(self.lbl_font)

        #colors for hr
        palette = self.hr_lbl.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
        self.hr_lbl.setPalette(palette)
        self.hr_lbl.setFixedWidth(self.lbl_width)
        self.hr_lbl.setAlignment(self.lbl_alignment)
        
        palette = self.pow_lbl.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("black"))
        self.pow_lbl.setPalette(palette)
        self.pow_lbl.setFixedWidth(self.lbl_width)
        self.pow_lbl.setAlignment(self.lbl_alignment)
        
        palette = self.cad_lbl.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("blue"))
        self.cad_lbl.setPalette(palette)
        self.cad_lbl.setFixedWidth(self.lbl_width)
        self.cad_lbl.setAlignment(self.lbl_alignment)
        
        #buttons
        self.connect_btn.clicked.connect(self.connect)
        self.start_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.stop_btn.clicked.connect(self.stop)
        self.done_btn.clicked.connect(self.done)
        
        #place holder for plots (hr, cadence and power)
        self.hr_plot = None 
        self.power_plot = None 
        self.cadence_plot = None 
        self.workout = Workout(self._set_hr_label, self._set_power_label, self._set_cad_label)
       
    def connect(self):
        self.parent.statusBar().showMessage('Connecting')
        self.workout.connect()
        self.hr_plot.connect(self.workout)
        self.power_plot.connect(self.workout)
        self.cadence_plot.connect(self.workout)

    def start(self):
        self.parent.statusBar().showMessage('Started')
        self.workout.start()
        self.hr_plot.start(self.workout)
        self.power_plot.start(self.workout)
        self.cadence_plot.start(self.workout)
        self.pause_btn.setDisabled(True)
        self.start_btn.setDisabled(False)
        self.done_btn.setDisabled(False)

    def pause(self):
        self.parent.statusBar().showMessage('Paused')
        self.paused = self.workout.pause()
        self.power_plot.pause()
        self.cadence_plot.pause()
        
    def stop(self):
        self.parent.statusBar().showMessage('Stopped')
        self.workout.stop()
        self.hr_plot.stop()
        self.power_plot.stop()
        self.cadence_plot.stop()

    def done(self):
        self.parent.statusBar().showMessage('Done')
        self.workout.done()

    def _render_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.done_btn)
        self.layout.addLayout(button_layout)

    def _render_plots(self):
        hrm_layout = QStackedLayout(self)
        hrm_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.layout.addLayout(hrm_layout)
        self.hr_plot = Plot("Heart Rate", 'bpm', "BPM", (60, 150), 'red', 'lightcoral', self._set_hr_label)
        hrm_layout.addWidget(self.hr_plot.plot())
        hrm_layout.addWidget(self.hr_lbl)
        hrm_layout.setCurrentIndex(1)

        power_layout = QStackedLayout(self)
        power_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.layout.addLayout(power_layout)
        self.power_plot = Plot("Power", 'Watts', "Watts", (200, 250), "green", 'palegreen', self._set_power_label)
        power_layout.addWidget(self.power_plot.plot())
        power_layout.addWidget(self.pow_lbl)
        power_layout.setCurrentIndex(1)

        cadence_layout = QStackedLayout(self)
        cadence_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.layout.addLayout(cadence_layout)
        self.cadence_plot = Plot("Cadence", 'rpm', "RPM", (70, 120), "blue", 'lightskyblue', self._set_cad_label)
        cadence_layout.addWidget(self.cadence_plot.plot())
        cadence_layout.addWidget(self.cad_lbl)
        cadence_layout.setCurrentIndex(1)

    def _set_hr_label(self, value):
        self.hr_lbl.setText(f"{value}")
    
    def _set_power_label(self, value):
        self.pow_lbl.setText(f"{value}")
    
    def _set_cad_label(self, value):
        self.cad_lbl.setText(f"{value}")

    def render(self):
        self.layout = QVBoxLayout(self)
        self._render_buttons()
        self._render_plots()

        self.parent.statusBar().showMessage('Ready')

        