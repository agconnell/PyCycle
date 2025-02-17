
import sys
import asyncio


from PySide6.QtWidgets import QApplication, QMainWindow
from asyncqtpy import QEventLoop

from src.ui import UI


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PyCycle!")
        self.setMinimumSize(1344, 756)

        self.ui = UI(self)
        self.setCentralWidget(self.ui)
        self.ui.render()

if __name__ == '__main__':  
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        sys.exit(loop.run_forever())