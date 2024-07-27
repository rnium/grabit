from datetime import datetime, timezone
from typing import List, Any, Callable
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from app.utils.exceptions.logging_exceptions import TaskManagerBusy, TaskManagerOff
import inspect
import asyncio
import enum

class LogLevel(str, enum.Enum):
    success = 'success'
    warning = 'warning'
    error = 'error'


class Log:
    def __init__(self, message: str, nowat: int = 0, total: int = 0, level: LogLevel = LogLevel.success):
        self.time = datetime.now(timezone.utc)
        self.message = message
        self.nowat = nowat
        self.total = total
        self.level = level


    @property
    def data(self):
        return {
            'time': self.time.isoformat(),
            'message': self.message,
            'level': self.level,
            'nowat': self.nowat,
            'total': self.total,
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
    
    def stop(self):
        if not self.is_busy:
            raise TaskManagerOff()
        self.__is_running = False

    async def __initiate_task(self):
        self.__is_running = True
        self.__start_time = datetime.now(timezone.utc)
        await self.add_log(Log(message='Task initiated'))
    
    async def __finish_task(self):
        seconds_elapsed = (datetime.now(timezone.utc) - self.__start_time).total_seconds()
        self.__is_running = False
        self.__start_time = None
        await self.add_log(Log(message='Task finished in {} seconds'.format(seconds_elapsed)))
    
    async def execute_task(self, executable: Callable, *args, **kwargs):
        if self.is_busy:
            raise TaskManagerBusy
        await self.__initiate_task()
        try:
            if inspect.iscoroutinefunction(executable):
                await executable(*args, *kwargs)
            else:
                executable(*args, *kwargs)   
        except Exception as e:
            self.add_log(Log(message='An unexpected error occurred. Details: {}'.format(str(e)), level=LogLevel.error))
        await self.__finish_task()
    
    def add_socket(self, socket: WebSocket):
        self.__connections.append(socket)
    
    def remove_socket(self, socket: WebSocket):
        if socket in self.__connections:
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
        await asyncio.sleep(0.1)
        


