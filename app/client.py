#!/usr/bin/env python3

# Python modules
import asyncio
import json
import logging

# Local modules
from logger import *

class Conn:
    """Async class to manage the connection to PHD2"""
    def __init__(self):
        self._stream_writer = None
        self._stream_reader = None
        self._terminator = b'\r\n'
        self._response = ''
        self._timeout = 3
        self._logger = logging.getLogger(f'{LOGGING_NAME}.{self.__class__.__name__}')

    async def connect(self, host, port):
        """Connects to a ip and port"""
        self._logger.debug('Connecting to PHD2')
        future = asyncio.open_connection(host, int(port))
        # Wait for timeout
        try:
            self._stream_reader, self._stream_writer = await asyncio.wait_for(
                future,
                timeout=self._timeout
            )
        except asyncio.TimeoutError:
            self._logger.debug('Socket timeout trying to conenct')
            raise
        except OSError:
            self._logger.debug('PHD2 server is not on or PHD2 is not started')
            raise
        
        return None

    async def disconnect(self):
        """Disconnect from the ip and port"""
        # Check if writer is init
        if self.is_connected:
            self._logger.debug('Disconnecting from PHD2')
            self._stream_writer.close()
            await self._stream_writer.wait_closed()

            # Reset variables
            self.reset()

        return None
        
    def reset(self):
        """Resets the stream parameters"""
        self._logger.debug('Resetting stream')
        self._stream_reader = self._stream_writer = None
        return None

    @property
    def is_connected(self):
        return self._stream_writer is not None and self._stream_reader is not None

    @property
    def response(self):
        return self._response

    async def send_msg(self, msg):
        """Sends a message over the connection"""
        self._logger.debug('Sending message')
        msg = msg.encode()
        self._stream_writer.write(msg)
        await self._stream_writer.drain()

        return None
        
    async def recv_msg(self):
        """Receives a message over the connection"""
        self._logger.debug('Receiving message')
        response = await self._stream_reader.readline()
        self._response = response.decode()

        return self._response

class Client:
    """Class for interacting with PHD2 guider"""
    def __init__(self, host='0.0.0.0', port=4400):
        self._host = host
        self._port = port
        self._conn = None
        self._initial_data = None
        self._logger = logging.getLogger(f'{LOGGING_NAME}.{self.__class__.__name__}')

    async def connect(self):
        """Connect to PHD2"""
        self._logger.debug('Attempting to connect to PHD2')
        await self.disconnect()
        try:
            self._conn = Conn()
            await self._conn.connect(self._host, self._port)
            self._logger.info(f'Connected to PHD2 at {self._host} {self._port}')

        except Exception:
            self._logger.debug('Could not connect to PHD2')
            await self.disconnect()
            raise
        
        return None
    
    async def disconnect(self, clean=True):
        """Disconnect from PHD"""
        if not clean:
            self._logger.debug('Not a clean disconnect from PHD2')
            self._conn = None
            self._initial_data = None

        elif self._conn is not None and clean:
            self._logger.debug('Disconnecting from PHD2')
            await self._conn.disconnect()
            self._conn = None
            self._initial_data = None
            
        return None

    @staticmethod
    def _build_jsonrpc(method, params, id):
        """Build the JSON payload to communicate to PHD"""
        jsonrpc = {
            'method': method,
            'id': id
        }
        if params is not None:
            if isinstance(params, (list, dict)):
                jsonrpc['params'] = params
            else:
                # Single parameter
                jsonrpc['params'] = [params]
        jsonrpc = json.dumps(jsonrpc, separators=(',',':'))
        
        return jsonrpc

    async def comm(self, method, id=1, params=None):
        """Communicate to PHD2 server"""
        self._logger.debug('Communicating to PHD2')
        jsonrpc = self._build_jsonrpc(method, params, id)

        try:
            await self._conn.send_msg(jsonrpc + '\r\n')
        except Exception:
            # BrokenPipeError, ConnectionResetError
            self._logger.critical('Connection was lost, resetting')
            await self.disconnect(clean=False)
            raise

        return None
    
    @property
    def initial_data(self):
        return self._initial_data

    @initial_data.setter
    def initial_data(self, value):
        """Sets the value for initial data"""
        self._logger.info('Got initial information')
        self._initial_data = value
        return None
    
    @property
    def is_connected(self):
        """Returns true if _conn is not None and is connected"""
        return self._conn is not None and self._conn.is_connected

    async def get_responses(self):
        """Tries to get responses and returns None if not"""
        self._logger.debug('Getting response from PHD2')
        response = await self._conn.recv_msg()
        response = response.strip('\r\n')

        # Return empty if response is empty
        if response is None or response == '':
            return None

        # If valid response
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            self._logger.warning(f'Could not parse response to json {response}')
            return None
    
        return response
