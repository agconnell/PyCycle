import asyncio
from bleak import BleakClient

async def send_data(address, characteristic_uuid, data_to_send):
    async with BleakClient(address, timeout=60) as client:
        try:
            await client.write_gatt_char(characteristic_uuid, data_to_send, response=True)
            print(f"Data sent: {data_to_send}")
        except Exception as e:
            print(f"Error sending data: {e}")

async def main():
    address = "CB:E1:30:26:F4:EE" # Replace with the actual device address
    characteristic_uuid = "00002a37-0000-1000-8000-00805f9b34fb" # Replace with the actual characteristic UUID
    # data format -- 'sensor_contact', 'bpm', 'rr_interval', 'energy_expended'
    msg = "{}{}{}{}".format(1, 60, 2, 120)
    data_to_send = bytes(msg, 'utf-8')  # Example data as bytes

    await send_data(address, characteristic_uuid, data_to_send)

if __name__ == "__main__":
    asyncio.run(main())