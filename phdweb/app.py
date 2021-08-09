#!/usr/bin/env python3

# Python modules
import asyncio
import logging
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Local modules
from client import Client
from logger import *

# Sources
"""
https://github.com/OpenPHDGuiding/phd2/wiki/EventMonitoring
"""

# Constants
POLL_INTERVAL = 1 # Seconds
STREAM_INTERVAL = 0.1 # Seconds
CONNECT_INTERVAL = 3 # Seconds
HEARTBEAT_TIMEOUT = 1 # Seconds
HEARTBEAT_EXPECTED = {'heartbeat': 'pong'}
PHD2_QUERIES = [
    'get_current_equipment',
    'get_cooler_status',
    'get_connected'
]

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
    
    async def send_heartbeat(self, websocket: WebSocket):
        """Heartbeat ping/pong to keep connection"""
        msg = {'heartbeat': 'ping'}
        try:
            # Create timeout for sending heartbeat
            future = websocket.send_json(msg)
            await asyncio.wait_for(future, timeout=HEARTBEAT_TIMEOUT)

            # Create timeout for receiving heartbeat
            future = websocket.receive_json()
            heartbeat = await asyncio.wait_for(future, timeout=HEARTBEAT_TIMEOUT)

            # If the heartbeat doesn't match, then raise
            if heartbeat != HEARTBEAT_EXPECTED:
                print(f'DIDNT GET HEARTBESt RIGHT {heartbeat}')
                raise asyncio.TimeoutError

        except asyncio.TimeoutError:
            self._logger.debug('Heartbeat was not successful')
            raise WebSocketDisconnect
        
        return None
        
    async def broadcast(self, msg: str):
        """Broadcase to active connections"""
        for connection in self._active_connections:
            await connection.send_json(msg)

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
    """Returns the web page template"""
    return templates.TemplateResponse('index.html', {'request': request})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """Handles incoming websocket connections and reads from queue"""
    logger.info(f'Accepting client #{client_id}')
    await manager.connect(websocket)
    # TODO Send intial data
    while True:
        try:
            await manager.send_heartbeat(websocket)
            data = await q.get_nowait()
            await manager.broadcast(data)
            q.task_done()

        except asyncio.QueueEmpty:
            # Nothing in the queue to send so continue
            continue

        except WebSocketDisconnect:
            logger.info(f'Client #{client_id} left')
            manager.disconnect(websocket)
            return None

async def stream():
    """Main streaming loop for PHD"""
    while True:
        if phd_client.is_connected and manager.active_connections:
            response = await phd_client.get_responses()
            if response is not None: 
            # Add to the websocket queue
            # If it is the initial data, put in variable
                if response.get('Event') == 'Version':
                    phd_client.initial_data = response
                q.put_nowait(response)

        await asyncio.sleep(STREAM_INTERVAL)
    
    return None

async def poll():
    """Polls PHD2 with specific queries"""
    while True:
        for rpc in PHD2_QUERIES:
            if phd_client.is_connected and manager.active_connections:
                try:
                    await phd_client.comm(rpc, rpc)
                except Exception as e:
                    await phd_client.disconnect(clean=False)
                
            await asyncio.sleep(POLL_INTERVAL)

    return None

async def connection():
    """Manages the connection to PHD2"""
    while True:
        if not phd_client.is_connected and manager.active_connections:
            try:
                await phd_client.connect()
            except Exception as e:
                # TODO Add error packet to send over to let the user know cannot connect
                logger.warning(f'Could not connect to PHD2, trying again in {CONNECT_INTERVAL} seconds')
                await asyncio.sleep(CONNECT_INTERVAL)

        elif phd_client.is_connected and not manager.active_connections:
            await phd_client.disconnect()

        await asyncio.sleep(POLL_INTERVAL)
    
    return None
            
@app.on_event('startup')
async def startup_event():
    """Runs on app startup"""
    # Create tasks
    logger.info('Starting app')
    asyncio.create_task(connection())
    asyncio.create_task(stream())
    asyncio.create_task(poll())
    return None



        
