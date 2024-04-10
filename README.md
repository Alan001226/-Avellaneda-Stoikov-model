# Avellaneda & Stoikov model in Crypto Market

This is a simplified version of Avellaneda & Stoikov model. We used 5 level bid/ask data from OKEX API, and back test if the AS model works under high frequency crypto market.

## Data
### data_recorder.py
In this file, we utilized the WebSocket service provided by OKEX (wss://ws.okx.com:8443/ws/v5/public) to subscribe the level data (bid/ask) at a tick level frequence. Noted that we add a 1 second timeout after each receiving, hence the actual data is second-level. (Noted that the frequency is not precisely second level and the timeout setting could be completely unnessary if you prefer higher level data).
