import socket
import json
import time
import asyncio
import logging

from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from client import Client
from logger import *

# https://github.com/OpenPHDGuiding/phd2/wiki/EventMonitoring
POLL_INTERVAL = 2 # Seconds

PHD2_QUERIES = {
    'get_current_equipment': 'get_current_equipment',
    'get_cooler_status': 'get_cooler_status',
    'get_connected': 'get_connected'
}

# Configure logging
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(f'{LOGGING_NAME}')
# Set up queue and fastapi
q = asyncio.Queue()
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

# Class for managing all websocket connections
class ConnectionManager:
    """Connection class for active connection handling"""
    def __init__(self):
        self._active_connections: List[WebSocket] = []
        self._logger = logging.getLogger(f'{LOGGING_NAME}.ConnectionManager')
        return None
    
    async def connect(self, websocket: WebSocket):
        """Accept connection to websocket"""
        self._logger.debug('Accepting connection')
        await websocket.accept()
        self._active_connections.append(websocket)
        return None
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect connection from websocket"""
        self._logger.debug('Disconnecting client')
        self._active_connections.remove(websocket)
        return None
    
    async def broadcast(self, msg: str):
        """Broadcase to active connections"""
        for connection in self._active_connections:
            try:
                await connection.send_json(msg)
            except Exception as e:
                self._logger.error(e.__class__.__name__, e)
                self._active_connections.remove(connection)
        return None

    @property
    def active_connections(self):
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
    try:
        while True:
            data = await q.get()
            await manager.broadcast(data)
            q.task_done()

    except Exception as e:
        logger.critical(e.__class__.__name__)
        logger.critical(f'Client #{client_id} left')
        manager.disconnect(websocket)


async def stream():
    """Main streaming loop for PHD"""
    while True:
        logger.debug(phd_client.is_connected)
        if phd_client.is_connected and manager.active_connections:
            response = await phd_client.get_responses()
            logger.critical(response)
            if response is None: 
                await asyncio.sleep(1)
                continue
            # Add to the websocket queue
            # If it is the initial data, put in variable
            if response.get('Event') == 'Version':
                phd_client.initial_data = response
            q.put_nowait(response)

        await asyncio.sleep(0.1)

async def poll():
    while True:
        logger.debug('Polling phd2')
        for rpc in PHD2_QUERIES.items():
            await asyncio.sleep(1)
            if phd_client.is_connected and manager.active_connections:
                (method, id) = rpc
                try:
                    await phd_client.comm(method, id)
                except Exception as e:
                    continue

async def connection():
    while True:
        if not phd_client.is_connected and manager.active_connections:
            try:
                await phd_client.connect()
            except Exception as e:
                logger.warning('Could not connect to PHD2, try again in 3')
                await asyncio.sleep(3)

        elif phd_client.is_connected and not manager.active_connections:
            await phd_client.disconnect()
        await asyncio.sleep(1)
            
@app.on_event('startup')
async def startup_event():
    """Runs on app startup"""
    # Create tasks
    logger.info('Creating tasks')
    asyncio.create_task(connection())
    asyncio.create_task(stream())
    asyncio.create_task(poll())
    return None



        
