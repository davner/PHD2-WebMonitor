import socket
import json
import time
import asyncio

from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from client import Client

# https://github.com/OpenPHDGuiding/phd2/wiki/EventMonitoring
POLL_INTERVAL = 2 # Seconds

""" PHD2 client uses
- stop_capture
- get_app_state
- loop
- get_exposure
- set_connected, True or False
- set_profile, profile_id
- set_paused, True or False
- get_settling
"""

PHD2_QUERIES = {
    'get_current_equipment': 'get_current_equipment',
    'get_cooler_status': 'get_cooler_status',
    'get_connected': 'get_connected'
}

q = asyncio.Queue()
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

# Class for managing all websocket connections
class ConnectionManager:
    """Connection class for active connection handling"""
    def __init__(self):
        self._active_connections: List[WebSocket] = []
        return None
    
    async def connect(self, websocket: WebSocket):
        """Accept connection to websocket"""
        print('GOT NEW CONNECTION')
        await websocket.accept()
        self._active_connections.append(websocket)
        return None
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect connection from websocket"""
        print('A client has left')
        self._active_connections.remove(websocket)
        return None
    
    async def broadcast(self, msg: str):
        """Broadcase to active connections"""
        for connection in self._active_connections:
            try:
                await connection.send_json(msg)
            except Exception as e:
                print(f'ERROR: {e}')
                self.disconnect(connection)
        return None

    @property
    def has_connections(self):
        """Return active connection"""
        return self._active_connections

manager = ConnectionManager()
phd_client = Client()
templates = Jinja2Templates(directory='templates')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """Handles incoming websocket connections and reads from queue"""
    await manager.connect(websocket)
    print(len(manager._active_connections))
    try:
        while True:
            data = await q.get()
            await manager.broadcast(data)
            q.task_done()

    except Exception:
        print(f'Client #{client_id} left')
        manager.disconnect(websocket)
            
async def stream_responses():
    """Main polling loop for PHD"""
    while True:
        # If active connections is empty and it is connected to phd2

        if not manager.has_connections and phd_client.is_connected:
            await phd_client.disconnect()
        
        elif manager.has_connections and not phd_client.is_connected:
            try:
                print('Connecting to PHD server')
                await phd_client.connect()

            except Exception:
                print('ERROR: Cannot connect, please start PHD and enable server. Will try again in 3 seconds ...')
                await asyncio.sleep(3)
                pass

        elif phd_client.is_connected:
            response = await phd_client.get_responses()
            # Add to the websocket queue
            if response is not None: 
                # If it is the initial data, put in variable
                if response.get('Event') == 'Version':
                    phd_client.initial_data = response
                    
                q.put_nowait(response)

        await asyncio.sleep(0.1)

async def poll():
    while True:
        if manager.has_connections and phd_client.is_connected:
            for rpc in PHD2_QUERIES.items():
                (method, id) = rpc
                try:
                    await phd_client.comm(method, id)
                except Exception:
                    pass
                await asyncio.sleep(1)
        await asyncio.sleep(1)

def main():
    asyncio.create_task(stream_responses())
    asyncio.create_task(poll())

    return None
            
@app.on_event('startup')
async def startup_event():
    """Runs on app startup"""

    main()
    return None



        
