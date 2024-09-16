import websocket


def on_message(ws, message):
    print("Received:", message)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws):
    print("Connection closed")


def on_open(ws):
    print("Connection opened")
    ws.send('{"test": "data"}')  # Send a simple JSON payload


ws = websocket.WebSocketApp(
    "ws://genie:8000/run_simulation",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.on_open = on_open
ws.run_forever()
