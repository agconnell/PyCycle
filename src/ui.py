'''Main UI of the application'''

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QMessageBox
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent
from src.plot import Plot

from src.workout import Workout
from config.config import DISCONNECTED, CONNECTED, RUNNING, STOPPED, DONE

class UI(QWidget):
    '''Main UI of the application'''
    lbl_font = QFont("Arial", 46, QFont.Bold)
    lbl_width = 100
    lbl_alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    btn_font = QFont("Arial", 12, QFont.Bold)
    
    gray  = QColor("gray")
    red   = QColor("red")
    green = QColor("green")
    blue  = QColor("blue")
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.status = DISCONNECTED
        self.i = 0
        self.layout = QVBoxLayout(self)
        self.timer = QTimer(self)

        #buttons labels and ui stuff
        self.connect_btn = QPushButton("Pair")
        self.start_btn = QPushButton("Start")
        self.done_btn = QPushButton("Done")

        self.connect_btn.setFont(self.btn_font)
        self.start_btn.setFont(self.btn_font)
        self.done_btn.setFont(self.btn_font)

        self.start_btn.setDisabled(True)
        self.done_btn.setDisabled(True)

        self.hr_lbl = QLabel("--")
        self.hr_lbl.setFont(self.lbl_font)

        self.pow_lbl = QLabel("--")
        self.pow_lbl.setFont(self.lbl_font)

        self.cad_lbl = QLabel("--")
        self.cad_lbl.setFont(self.lbl_font)

        #colors for hr
        self.red = self.hr_lbl.palette()
        self.red.setColor(QPalette.ColorRole.WindowText, QColor("gray"))
        self.hr_lbl.setPalette(self.red)
        self.hr_lbl.setFixedWidth(self.lbl_width)
        self.hr_lbl.setAlignment(self.lbl_alignment)
        
        self.black = self.pow_lbl.palette()
        self.black.setColor(QPalette.ColorRole.WindowText, QColor("gray"))
        self.pow_lbl.setPalette(self.black)
        self.pow_lbl.setFixedWidth(self.lbl_width)
        self.pow_lbl.setAlignment(self.lbl_alignment)
        
        self.blue = self.cad_lbl.palette()
        self.blue.setColor(QPalette.ColorRole.WindowText, QColor("gray"))
        self.cad_lbl.setPalette(self.blue)
        self.cad_lbl.setFixedWidth(self.lbl_width)
        self.cad_lbl.setAlignment(self.lbl_alignment)
        
        #buttons
        self.connect_btn.clicked.connect(self.connect)
        self.start_btn.clicked.connect(self.start)
        self.done_btn.clicked.connect(self.done)
        
        #place holder for plots (hr, cadence and power)
        self.hr_plot = None 
        self.power_plot = None 
        self.cadence_plot = None 
        self.workout = Workout(self._set_hr_label, self._set_power_label, self._set_cad_label)

    def update(self):
        '''Update the UI with the latest data from the LRUs'''
        self.i += 1
        if self.status < DONE:
            # print(f"UI Update {self.i}")
            self.status = self.workout.get_status()
            if self.status == DISCONNECTED:
                self.connect_btn.setEnabled(True)
                self.start_btn.setEnabled(False)
                self.done_btn.setEnabled(True)
            elif self.status == CONNECTED:
                self.parent.statusBar().showMessage('Connected - ready to start!')
                self.connect_btn.setEnabled(False)
                self.start_btn.setEnabled(True)
                self.done_btn.setEnabled(False)
            elif self.status == RUNNING:
                self.start_btn.setText('Stop')
                self.parent.statusBar().showMessage('Running!')
                self.connect_btn.setEnabled(False)
                self.start_btn.setEnabled(True)
                self.done_btn.setEnabled(False)
                self.power_plot.update()
                self.hr_plot.update()
                self.cadence_plot.update()
            elif self.status == STOPPED:
                self.start_btn.setText('Resume')
                self.parent.statusBar().showMessage('Stopped - hit Done to save and exit')
                self.connect_btn.setEnabled(False)
                self.start_btn.setEnabled(True)
                self.done_btn.setEnabled(True)

            if self.status > DISCONNECTED:
                self.hr_lbl.setText(str(self.workout.get_last_value('bpm')))
                self.pow_lbl.setText(str(self.workout.get_last_value('Watts')))
                self.cad_lbl.setText(str(self.workout.get_last_value('rpm')))

    def connect(self):
        '''connect to the configured LRUs'''
        self.parent.statusBar().showMessage('Connecting')
        self.workout.connect()
        self.hr_plot.connect(self.workout)
        self.power_plot.connect(self.workout)
        self.cadence_plot.connect(self.workout)

    def start(self):
        '''start the wrokout or resume if paused'''
        hrm_p = self.hr_lbl.palette()
        pow_p = self.pow_lbl.palette()
        cad_p = self.cad_lbl.palette()
    
        if self.workout.status == RUNNING:
            hrm_p.setColor(QPalette.ColorRole.WindowText, QColor("gray"))
            pow_p.setColor(QPalette.ColorRole.WindowText, QColor("gray"))
            cad_p.setColor(QPalette.ColorRole.WindowText, QColor("gray"))
        else:
            hrm_p.setColor(QPalette.ColorRole.WindowText, QColor("red"))
            pow_p.setColor(QPalette.ColorRole.WindowText, QColor("green"))
            cad_p.setColor(QPalette.ColorRole.WindowText, QColor("blue"))
            
        self.hr_lbl.setPalette(hrm_p)
        self.pow_lbl.setPalette(pow_p)
        self.cad_lbl.setPalette(cad_p)

        self.workout.start()

    def done(self):
        '''complete the workout'''
        self.parent.statusBar().showMessage('Done')
        self.workout.done()
        self.parent.exit_app()

    def _render_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.done_btn)
        self.layout.addLayout(button_layout)

    def _render_plots(self):
        hrm_layout = QStackedLayout(self)
        hrm_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        hrm_layout.setSpacing(30)
        self.layout.addLayout(hrm_layout)
        self.hr_plot = Plot("Heart Rate", 'bpm', "BPM", (50, 150), 'red', 'lightcoral', self._set_hr_label)
        hrm_layout.addWidget(self.hr_plot.plot())
        hrm_layout.addWidget(self.hr_lbl)
        hrm_layout.setCurrentIndex(1)

        power_layout = QStackedLayout(self)
        power_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        power_layout.setSpacing(10)
        self.layout.addLayout(power_layout)
        self.power_plot = Plot("Power", 'Watts', "Watts", (0, 250), "green", 'palegreen', self._set_power_label)
        power_layout.addWidget(self.power_plot.plot())
        power_layout.addWidget(self.pow_lbl)
        power_layout.setCurrentIndex(1)

        cadence_layout = QStackedLayout(self)
        cadence_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        cadence_layout.setSpacing(60)
        self.layout.addLayout(cadence_layout)
        self.cadence_plot = Plot("Cadence", 'rpm', "RPM", (0, 120), "blue", 'lightskyblue', self._set_cad_label)
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
        '''render the main part of the UI'''
        self._render_buttons()
        self._render_plots()

        self.parent.statusBar().showMessage('Ready')  
        self.timer.timeout.connect(self.update)
        self.timer.start(250)  

    def quit_alert(self):
        '''Prompt the user before quitting the app'''
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Quit PyCycle?")
        msg_box.setText("Save and Exit?")
        msg_box.setIcon(QMessageBox.Icon.Information)  # Optional: Set icon
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Optional: Set buttons
        return msg_box.exec() == QMessageBox.Ok