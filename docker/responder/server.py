import asyncio
import websockets
import socket

async def handler(websocket, path):
    while True:
        message = f"Hello from {socket.gethostbyname(socket.gethostname())}!"
        await websocket.send(message)
        await asyncio.sleep(5)

start_server = websockets.serve(handler, "0.0.0.0", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
