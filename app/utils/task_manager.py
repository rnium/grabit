from datetime import datetime, timezone
from typing import List, Any, Callable
from fastapi import WebSocket, WebSocketDisconnect
from app.utils.exceptions.logging_exceptions import TaskManagerBusy, TaskManagerOff
import inspect
import asyncio
import enum

class LogLevel(str, enum.Enum):
    success = 'success'
    warning = 'warning'
    error = 'error'


class Log:
    def __init__(self, message: str, progress: float = 0, level: LogLevel = LogLevel.success):
        self.time = datetime.now(timezone.utc)
        self.message = message
        self.progress = progress
        self.level = level
        
    @property
    def data(self):
        return {
            'time': self.time.isoformat(),
            'message': self.message,
            'level': self.level,
            'progress': self.progress 
        }


class TaskManager:
    def __init__(self):
        self.__is_running = False
        self.__start_time = None
        self.__connections: List[WebSocket] = []
        self.__log_queue = asyncio.Queue(100)

    @property
    def is_busy(self):
        return self.__is_running

    async def __initiate_task(self):
        self.__is_running = True
        self.__start_time = datetime.now(timezone.utc)
        await self.add_log(Log('Task initiated'))
    
    async def __finish_task(self):
        seconds_elapsed = (datetime.now(timezone.utc) - self.__start_time).total_seconds()
        self.__is_running = False
        self.__start_time = None
        await self.add_log(Log('Task finished in {} seconds'.format(seconds_elapsed)))
    
    async def execute_task(self, executable: Callable, *args, **kwargs):
        if self.is_busy:
            raise TaskManagerBusy
        await self.__initiate_task()
        if inspect.iscoroutinefunction(executable):
            await executable(*args, *kwargs)
        else:
            executable(*args, *kwargs)
        await self.__finish_task()
    
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
        await self.send_logs()
        await asyncio.sleep(0.2)
        


