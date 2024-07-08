from datetime import datetime, timezone
from typing import List, Any
from fastapi import WebSocket, WebSocketDisconnect
from app.utils.exceptions.logging_exceptions import TaskManagerBusy, TaskManagerOff
import asyncio


class Log:
    def __init__(self, message: str, progress: float = 0):
        self.time = datetime.now(timezone.utc)
        self.message = message
        self.progress = progress
        
    @property
    def data(self):
        return {
            'time': self.time.isoformat(),
            'message': self.message,
            'progress': self.progress 
        }


class TaskManager:
    def __init__(self):
        self.__is_running = False
        self.__start_time = None
        self.__connections: List[WebSocket] = []
        self.__log_queue = asyncio.Queue(100)
        self.__task_argument = None
    
    @property
    def argument(self):
        return self.__task_argument
        
    async def initiate_task(self, argument: Any):
        if self.__is_running:
            raise TaskManagerBusy()
        self.__is_running = True
        self.__start_time = datetime.now(timezone.utc)
        self.__task_argument = argument
        await self.add_log(Log('Task initiated'))
    
    async def finish_task(self):
        if not self.__is_running:
            raise TaskManagerOff()
        seconds_elapsed = (datetime.now(timezone.utc) - self.__start_time).total_seconds()
        self.__is_running = False
        self.__start_time = None
        self.__task_argument = None
        await self.add_log(Log('Task finished in {} seconds'.format(seconds_elapsed)))
    
    def add_socket(self, socket: WebSocket):
        self.__connections.append(socket)
    
    def remove_socket(self, socket: WebSocket):
        self.__connections.remove(socket)
        
    def get_data(self, log: Log):
        return {
            **log.data,
            'running': self.__is_running
        }

    async def send_logs(self):
        if self.__connections:
            removable_sockets = []
            while not self.__log_queue.empty():
                log = await self.__log_queue.get()
                for socket in self.__connections:
                    try:
                        await socket.send_json(self.get_data(log))
                    except WebSocketDisconnect:
                        removable_sockets.append(socket)
            for socket in removable_sockets:
                self.remove_socket(socket)
    
    async def add_log(self, log: Log):
        await self.__log_queue.put(log)
        await asyncio.sleep(0.2)
        await self.send_logs()
        


