
import sys
import time
import asyncio


from PySide6.QtWidgets import QApplication, QMainWindow

from src.config_manager import ConfigManager
from src.config_manager import USER_NAME, WORKOUT_BY_POWER,TV_MODE,HR_ZONES,ROLLING_RESISTANCE,DRAG_COEFFICIENT,TRAINER_ID
from src.workout_manager import WorkoutManager
from src.ui import UI

import asyncio


class MainWindow(QMainWindow):
    config = ConfigManager()
    print(f'User name: {config.get(USER_NAME)}')

    # workout_manager = WorkoutManager()
    # workout_manager.start_workout()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PyCycle!")
        self.setMinimumSize(1344, 756)

        self.ui = UI(self)
        self.setCentralWidget(self.ui)
        self.ui.render()

if __name__ == '__main__':  
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())