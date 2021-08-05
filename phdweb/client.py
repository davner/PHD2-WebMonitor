#!/usr/bin/env python3

import asyncio
import json

class Conn:
    def __init__(self):
        self._buf = b''
        self._stream_writer = None
        self._stream_reader = None
        self._terminator = b'\r\n'
        self._response = ''
        self._timeout = 1

    async def connect(self, host, port):
        """Connects to a ip and port"""
        future = asyncio.open_connection(host, int(port))
        # Wait for timeout
        try:
            self._stream_reader, self._stream_writer = await asyncio.wait_for(
                future,
                timeout=self._timeout
            )
        except Exception:
            # Reset connection
            self._stream_reader = self._stream_writer = None 
            raise PHDError('Stream timeout')
        
        return None

    async def disconnect(self):
        """Disconnect from the ip and port"""
        # Check if writer is init
        if self.is_connected:
            self._stream_writer.close()
            await self._stream_writer.wait_closed()

            # Reset variables
            self._stream_reader = self._stream_writer = None

        return None
        
    @property
    def is_connected(self):
        return self._stream_writer is not None

    @property
    def response(self):
        return self._response

    async def send_msg(self, msg):
        """Sends a message over the connection"""
        msg = msg.encode()
        self._stream_writer.write(msg)
        await self._stream_writer.drain()

        return
        
    async def recv_msg(self):
        """Recieves a message over the connection"""
        response = await self._stream_reader.readline()
        self._response = response.decode()

        return self._response

class Client:
    """
    Class for interacting with PHD2 guider.

    Get/Set JSON-RPC
    """
    def __init__(self, host='localhost', port=4400):
        self._host = host
        self._port = port
        self._conn = None
        self._initial_data = None

    async def connect(self):
        """Connect to PHD"""
        await self.disconnect()
        try:
            self._conn = Conn()
            await self._conn.connect(self._host, self._port)
            print('Connected to {} {}'.format(self._host, self._port))

        except Exception:
            await self.disconnect()
            raise PHDError('Could not connect')
    
    async def disconnect(self):
        """Disconnect from PHD"""
        if self._conn is not None:
            await self._conn.disconnect()
            self._conn = None
        
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

    @staticmethod
    def _failed(response):
        return 'error' in response

    async def comm(self, method, id=1, params=None):
        jsonrpc = self._build_jsonrpc(method, params, id)

        #print('Sending --> {}'.format(jsonrpc))
        
        await self._conn.send_msg(jsonrpc + '\r\n')

        return None
    
    @property
    def initial_data(self):
        return self._initial_data

    @initial_data.setter
    def initial_data(self, value):
        """Sets the value for initial data"""
        self._initial_data = value
        return None
    
    @property
    def is_connected(self):
        return self._conn is not None and self._conn.is_connected

    async def get_responses(self):
        """Tries to get responses and returns None if not"""
        try:
            response = await self._conn.recv_msg()
            response = response.strip('\r\n') # Can't do this above for await
            #print(response)
        except Exception:
            print('Nothing on the line, sleeping')
            return None
        
        if response is not None:
            try:
                response = json.loads(response)
                #print('Received --> {}'.format(response))
            except json.JSONDecodeError:
                print('Could not unpack json from PHD')
                pass
            

        return response

class PHDError(Exception):
    """Base PHD error class"""
    def __init__(self, *args):
        if args:
            self._message = args[0]
        else:
            self._message = 'Generic PHD2 error'
    
    def __str__(self):
        return '{}'.format(self._message)
