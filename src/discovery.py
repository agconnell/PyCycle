"""
Scan/Discovery
--------------

Example showing how to scan for BLE devices.

Updated on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>

"""

import sys
import argparse
import asyncio
from PySide6.QtAsyncio import QAsyncioEventLoop

from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar, QLabel
from bleak import BleakScanner

class MainWindow(QMainWindow):
    '''Entry point of the application'''


    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Charts!")
        self.setMinimumSize(800, 600)

    async def main(args: argparse.Namespace):
        print("scanning for 5 seconds, please wait...")

        devices = await BleakScanner.discover(
            return_adv=True,
            service_uuids=args.services,
            cb=dict(use_bdaddr=args.macos_use_bdaddr),
        )

        for d, a in devices.values():
            print()
            print(d)
            print("-" * len(str(d)))
            print(a)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--services",
        metavar="<uuid>",
        nargs="*",
        help="UUIDs of one or more services to filter for",
    )

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    args = parser.parse_args()

    app = QApplication([])
    loop = QAsyncioEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()