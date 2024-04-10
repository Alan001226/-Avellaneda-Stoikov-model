import asyncio
import websockets
import json
import hmac
import base64
import hashlib
import time
import csv
from datetime import datetime
import numpy as np

API_KEY = 'faec99ec-a5ba-4ceb-8949-8e3a9460a211'
SECRET_KEY = '8366A3936B5A9F859B0D9F1705B32860'
PASSPHRASE = '!DataRecorder123'




def get_timestamp():
    return str(time.time())

def generate_sign(message, secretKey):
    mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d).decode()

def check_list(list_a, level):
    ret_list = list()
    if len(list_a) == level:
        ret_list = list_a
    else:
        ret_list = list_a + [np.nan] * (level - len(list_a))
    ret_list = [float(x) for x in ret_list]
    return ret_list

async def login(url, API_KEY, SECRET_KEY, PASSPHRASE):
    login_message = {
            "op": "login",
            "args": [
                {
                    "apiKey": API_KEY,
                    "passphrase": PASSPHRASE,
                    "timestamp": get_timestamp(),
                    "sign": generate_sign(get_timestamp(), SECRET_KEY)
                }
            ]
        }
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps(login_message))
        response = await ws.recv()
        print(response)
async def order_book(url, currency_pair, timelen=10, filename="orderbook_data.csv", level=5):
    """
    Connects to a WebSocket server, subscribes to the order book channel for a specific currency pair,
    and records the order book data into a CSV file for a specified time period.

    Parameters:
    - url (str): The URL of the WebSocket server.
    - currency_pair (str): The currency pair to subscribe to.
    - timelen (int): The time limit (in seconds) for receiving messages. Default is 10 seconds.
    - filename (str): The name of the CSV file to store the order book data. Default is "orderbook_data.csv".
    - level (int): The number of levels to record in the order book. Default is 5.

    Returns:
    - None

    """
    try:
        async with websockets.connect(url, ping_timeout=60, ping_interval=25) as ws:
            # Subscribe to the order book channel
            await ws.send(json.dumps({
                "op": "subscribe",
                "args": [{"channel": "books5", "instId": currency_pair.upper()}]
            }))
            # subscribe_response = ws.recv()
            # if "connId" not in subscribe_response:
            #     print("Error in subscribing to the channel")
            #     return 0


            # Set the start and end time for recording data
            start_time = time.time()
            end_time = start_time + timelen 

            # Initialize CSV file with headers
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'Bid List','Bid Size List','Ask List','Ask Size List'])


            while time.time() <= end_time:
                try:
                    #response = await asyncio.wait_for(ws.recv(),timeout=1)
                    response = await ws.recv()
                    # await asyncio.sleep(1)  # Wait for 1 second before receiving the next message
                    message = json.loads(response)
                    # print(message)
                    if 'data' in message:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        data = message['data'][0]
                        # print(data)
                        # print("==="*20)
                        bids = data['bids']
                        asks = data['asks']
                        # print(asks)
                        with open(filename, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            bid_list = [f"{bid[0]}" for bid in bids]
                            bid_size_list = [f"{bid[1]}" for bid in bids]
                            ask_list = [f"{ask[0]}" for ask in asks]
                            ask_size_list = [f"{ask[1]}" for ask in asks]
                            #check if the list is of the correct length
                            bid_list = check_list(bid_list,level)
                            bid_size_list = check_list(bid_size_list,level)
                            ask_list = check_list(ask_list,level)
                            ask_size_list = check_list(ask_size_list,level)
                            writer.writerow([timestamp, bid_list, bid_size_list, ask_list, ask_size_list])
                except asyncio.TimeoutError:
                    print("Timeout error occurred")
                    # Time limit reached, exit the loop
                    break
            # unsubscribe from the channel
            ws.send(json.dumps({
                "op": "unsubscribe",
                "args": [{"channel": "books5", "sprdId": "ETH-USDT_ETH-USDT-SWAP"}]
            }))
            print("Unsubscribed from the channel")
    except Exception as e:
        print(f"Connection closed with error: {e}")


async def main():
    currency_pair = 'ETH-USDT'  # Specify the currency pair
    url = "wss://ws.okx.com:8443/ws/v5/public"  # OKEx WebSocket URL
    url_new =  "wss://ws.okx.com:8443/ws/v5/business"  # OKEx WebSocket URL Spread Channel
    # # log in to the server
    # await login(url, API_KEY, SECRET_KEY, PASSPHRASE)
    # record order book data
    print("Recording order book data...")
    await order_book(url, currency_pair,timelen=86400,filename="historical_ETHUSDT_orderbook_data_4.csv",level=5 )
    
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())
