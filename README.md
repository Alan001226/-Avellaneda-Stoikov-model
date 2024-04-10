# Avellaneda & Stoikov model in Crypto Market

This is a simplified version of Avellaneda & Stoikov model. We used 5 level bid/ask data from OKEX API, and back test if the AS model works under high frequency crypto market.

## Data (data_recorder.py)
### WebSocket Service for Data Recording

In this file, we utilized the WebSocket service provided by OKEX (wss://ws.okx.com:8443/ws/v5/public) to subscribe the level data (bid/ask) at a tick level frequence. Noted that we add a 1 second timeout after each receiving, by which we aimed to get the actual data in second-level. (But it didn't work and remained unfixed).

Here is the official document of OKEX WebSocket service: https://www.okx.com/docs-v5/en/#overview-websocket

### Sample Data

Here a piece of sample data:

| Timestamp           | Bid List                                      | Bid Size List                         | Ask List                                    | Ask Size List                          |
| ------------------- | --------------------------------------------- | ------------------------------------- | ------------------------------------------- | -------------------------------------- |
| 2024-03-07 00:00:26 | [3788.59, 3788.58, 3788.57, 3788.56, 3788.55] | [2.53871, 0.222, 0.482, 0.002, 0.002] | [3788.6, 3788.65, 3788.68, 3788.7, 3788.73] | [0.31, 0.002, 0.001, 0.001, 0.003]     |
| 2024-03-07 00:00:26 | [3788.59, 3788.58, 3788.57, 3788.56, 3788.55] | [1.93871, 0.222, 0.482, 0.002, 0.002] | [3788.6, 3788.65, 3788.68, 3788.7, 3788.73] | [0.31, 0.002, 0.001, 0.001, 0.003]     |
| 2024-03-07 00:00:26 | [3788.59, 3788.58, 3788.57, 3788.56, 3788.55] | [2.43871, 0.222, 0.482, 0.002, 0.002] | [3788.6, 3788.65, 3788.68, 3788.7, 3788.73] | [0.304722, 0.002, 0.001, 0.001, 0.003] |
| ...                 | ...                                           | ...                                   | ...                                         | ...                                    |

* Timestamp: current time stamp
* Bid List: 5 bid prices listed on the bid book (sorted from highest to lowest)
* Ask List: 5 ask prices listed on the ask book (sorted from lowest to highest)
* Bid Size List: the volume (size) of the bid limit order listed corresponding to the bid list
* Ask Size List: the volume (size) of the ask limit order listed corresponding to the ask list

