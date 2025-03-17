
import sys
import asyncio
import time

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtGui import QCloseEvent
from asyncqtpy import QEventLoop

from ui import UI


class MainWindow(QMainWindow):
    '''Main window of the application'''
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCycle!")
        self.setMinimumSize(1344, 756)

        self.ui = UI(self)
        self.setCentralWidget(self.ui)
        self.ui.render()

    def closeEvent(self, event: QCloseEvent):
        '''Propmt before close the application'''
        reply = QMessageBox.question(
            self,
            "Close Confirmation",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.ui.workout.done()
            time.sleep(1)
            event.accept()
            self.exit_app()
        else:
            event.ignore()

    def exit_app(self):
        '''Exit the application'''
        QApplication.instance().quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        sys.exit(loop.run_forever())