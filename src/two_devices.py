import argparse
import asyncio
import contextlib
import logging
from typing import Iterable

from bleak import BleakClient, BleakScanner


async def connect_to_device(
    lock: asyncio.Lock,
    by_address: bool,
    macos_use_bdaddr: bool,
    name_or_address: str,
    notify_uuid: str,
):
    """
    Scan and connect to a device then print notifications for 10 seconds before
    disconnecting.
    """
    logging.info("starting %s task", name_or_address)

    try:
        async with contextlib.AsyncExitStack() as stack:

            # Trying to establish a connection to two devices at the same time
            # can cause errors, so use a lock to avoid this.
            async with lock:
                logging.info("scanning for %s", name_or_address)

                if by_address:
                    device = await BleakScanner.find_device_by_address(
                        name_or_address, macos=dict(use_bdaddr=macos_use_bdaddr)
                    )
                else:
                    device = await BleakScanner.find_device_by_name(name_or_address)

                logging.info("stopped scanning for %s", name_or_address)

                if device is None:
                    logging.error("%s not found", name_or_address)
                    return

                client = BleakClient(device)

                logging.info("connecting to %s", name_or_address)

                await stack.enter_async_context(client)

                logging.info("connected to %s", name_or_address)

                # This will be called immediately before client.__aexit__ when
                # the stack context manager exits.
                stack.callback(logging.info, "disconnecting from %s", name_or_address)

            # The lock is released here. The device is still connected and the
            # Bluetooth adapter is now free to scan and connect another device
            # without disconnecting this one.

            def callback(_, data):
                logging.info("%s received %r", name_or_address, data)

            await client.start_notify(notify_uuid, callback)
            await asyncio.sleep(10.0)
            await client.stop_notify(notify_uuid)

        # The stack context manager exits here, triggering disconnection.

        logging.info("disconnected from %s", name_or_address)

    except Exception:
        logging.exception("error with %s", name_or_address)


async def main(
    by_address: bool,
    macos_use_bdaddr: bool,
    addresses: Iterable[str],
    uuids: Iterable[str],
):
    lock = asyncio.Lock()

    await asyncio.gather(
        *(
            connect_to_device(lock, by_address, macos_use_bdaddr, address, uuid)
            for address, uuid in zip(addresses, uuids)
        )
    )


if __name__ == "__main__":

    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    HRM_name = "HW706-0020070"
    HRM_ID = "0000180d-0000-1000-8000-00805f9b34fb"
    # BIKE_NAME = "KICKR CORE 470A"
    # BIKE_ID = "00001818-0000-1000-8000-00805f9b34fb"

    asyncio.run(
        main( True, True, (HRM_name ), (HRM_ID) )
    )