__version__ = "1.0.2"

import time
import asyncio
from bleak import BleakClient
from threading import Thread, Event
from queue import Queue

from typing import Optional, Tuple

from .middleware import Solver
from .models import BraccioConfig, BraccioCommand, BraccioPosition, CommandStatus, Wrist, Gripper

class Braccio(Thread):
    _TICK: float = 0.02
    CMD: str = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
    STATUS: str = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

    config: BraccioConfig

    solver: Solver
    _stop_event: Event
    _cmd_status: Optional[CommandStatus] 
    client: Optional[BleakClient]

    def __init__(self, config: BraccioConfig):
        Thread.__init__(self)

        self.config = config
        self.command_queue = Queue()
        self.solver = Solver()
        self._stop_event = Event()
        self._cmd_status = None
        self.client = None

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.stop()

    @property
    def connected(self) -> bool:
        return self.client.is_connected if self.client else False
    
    @staticmethod
    def get_cmd_string(command: BraccioCommand):
        return f"{command.toString()}|"

    @staticmethod
    def get_cmd_bytes(command: BraccioCommand):
        return Braccio.get_cmd_string(command).encode()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.loop.create_task(self.main()))

    def stop(self, timeout: float = 5):
        self._stop_event.set()
        self.join(timeout)

    def update(self, char, data: bytearray):
        recv = data.decode()
        self._cmd_status = CommandStatus(recv)

    async def main(self):
        while not self._stop_event.is_set():
            self.client = BleakClient(self.config.address)
            try:
                await self.client.connect()
                await self.client.start_notify(Braccio.STATUS, self.update)
            except Exception as e:
                pass

            while self.client.is_connected:
                if self._stop_event.is_set():
                    await self.client.disconnect()
                    return

                command = self.get_command()
                if command:
                    self._cmd_status = CommandStatus.EXECUTING
                    command_bytes = self.get_cmd_bytes(command)
                    while command_bytes:
                        payload = command_bytes[:20]
                        command_bytes = command_bytes[20:]
                        await self.client.write_gatt_char(
                            self.CMD,
                            payload
                        )

                await asyncio.sleep(self._TICK)

            await asyncio.sleep(self._TICK)

        if self.client:
            await self.client.disconnect()

    def add_command(self, command: BraccioCommand):
        self.command_queue.put(command)

    def get_command(self) -> Optional[BraccioCommand]:
        try:
            return self.command_queue.get_nowait()
        except Exception as e:
            return None
        
    def send_command(self, command: BraccioCommand, timeout: float = 10) -> Tuple[bool, CommandStatus, float]:
        self.add_command(command)
        t = 0

        while t < timeout:
            cmd_status = self._cmd_status
            if cmd_status and cmd_status is not CommandStatus.EXECUTING:
                self._cmd_status = None
                return (cmd_status is CommandStatus.OK, cmd_status, t)
                
            t += self._TICK
            time.sleep(self._TICK) 
        
        self._cmd_status = None
        return (False, CommandStatus.TIMEOUT, t)

    def move(self, x: float, y: float, z: float, wrist: Wrist = Wrist.HORIZONTAL, gripper: Gripper = Gripper.CLOSE, timeout: float = 10) -> Tuple[bool, CommandStatus, float]:
        try:
            _base, _shoulder, _elbow, _wrist = self.solver.move_to_position_cart(x, y, z)
        except Exception as e:
            return (False, CommandStatus.OUT_OF_RANGE, 0)
        
        return self.send_command(BraccioCommand.Move(BraccioPosition(_base, _shoulder, _elbow, _wrist, wrist, gripper)))
        
    def home(self) -> Tuple[bool, CommandStatus, float]:
        return self.send_command(BraccioCommand.Home())

    def on(self) -> Tuple[bool, CommandStatus, float]:
        return self.send_command(BraccioCommand.On())

    def off(self) -> Tuple[bool, CommandStatus, float]:
        return self.send_command(BraccioCommand.Off())

