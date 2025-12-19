from enum import Enum
from dataclasses import dataclass

from typing import Optional

class Wrist(Enum):
    HORIZONTAL = 90
    VERTICAL = 0

class Gripper(Enum):
    OPEN = 0
    CLOSE = 73

class Command(Enum):
    MOVE = "P"
    HOME = "H"
    TURN_ON = "1"
    TURNO_OFF = "0"

class CommandStatus(Enum):
    EXECUTING = "100"
    OK = "0"
    ERROR_1 = "1"
    ERROR_2 = "2"
    OUT_OF_RANGE = "3"
    TIMEOUT = "99"

@dataclass
class BraccioConfig:
    address: str

@dataclass
class BraccioPosition:
    base: float
    shoulder: float
    elbow: float
    wrist: float
    wrist_rotation: Wrist
    gripper: Gripper

    def toString(self):
        return f"{self.base},{self.shoulder},{self.elbow},{self.wrist},{self.wrist_rotation.value},{self.gripper.value}"

@dataclass
class BraccioCommand:
    command: Command
    position: Optional[BraccioPosition] = None

    @classmethod
    def Move(cls, position):
        return cls(Command.MOVE, position)
    
    @classmethod
    def Home(cls):
        return cls(Command.HOME)
    
    @classmethod
    def On(cls):
        return cls(Command.TURN_ON)
    
    @classmethod
    def Off(cls):
        return cls(Command.TURNO_OFF)

    def toString(self):
        pos_string = "," + self.position.toString() if self.position else ""
        return f"{self.command.value}{pos_string}"