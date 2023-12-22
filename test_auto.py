"""automated test for app"""
import os
import sys
import asyncio
import random
import logging
import json
import datetime
import time

from azure.cosmos import CosmosClient
from azure.iot.device.aio import IoTHubDeviceClient

logging.basicConfig(level=logging.ERROR)


url = os.environ["ACCOUNT_URI"]
key = os.environ["ACCOUNT_KEY"]
database_name = os.environ["DATABASE_NAME"]
container_name =  os.environ["CONTAINER_NAME"]

print(sys.version)


# Define connection string
connectionString = "HostName=yetanotheriothub.azure-devices.net;DeviceId=test;SharedAccessKey=ojuvSLucYlHq2ElvFr1bZuPGtLyJz5/uxAIoTNBt2qA=" # os.environ["DEVICE_CONNECTION_STRING"]

async def send_to_iot_hub(data):
    """sends data to iot hub"""
    try:
        # Create an instance of the IoT Hub Client class
        device_client = IoTHubDeviceClient.create_from_connection_string(connectionString)

        # Connect the device client
        await device_client.connect()

        #Send the message
        await device_client.send_message(data)
        print("Message sent to IoT Hub: %s", data)

        # Shutdown the client
        await device_client.shutdown()

    except Exception as e: # pylint: disable=broad-except
        print(e)

def main():
    """entry point"""
    # Generate random value
    temperature = random.randint(20, 50)
    # Generate data packet
    data={
        "device_id":"test",
        "temperature":temperature,
        "edge_time_stamp":str(datetime.datetime.now())
    }
    asyncio.run(send_to_iot_hub(data=json.dumps(data)))
    time.sleep(5)

    client = CosmosClient(url, {'masterKey': key}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        db = client.get_database_client(database_name)
        print(f'Database with id \'{database_name}\' was found')

        container = db.get_container_client(container_name)
        print(f'Container with id \'{container_name}\' was found')

        d = list(container.query_items(
                query=f'SELECT * FROM {container_name} c ORDER BY c._ts DESC OFFSET 0 LIMIT 1',
                enable_cross_partition_query=True
            ))

        msg = d[-1]['payload']
        print("Message received from Cosmos DB: %s", msg)

    except Exception as e:  # pylint: disable=broad-except
        print(e)

    assert data['device_id'] == msg['device_id']
    assert data['temperature'] == msg['temperature']
    assert data['edge_time_stamp'] == msg['edge_time_stamp']

    print("Test passed.")

if __name__ == '__main__':
    main()
