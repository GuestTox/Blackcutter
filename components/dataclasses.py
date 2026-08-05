from dataclasses import dataclass, field

@dataclass
class Visible: pass

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Velocity:
    x: int = 0
    y: int = 0

@dataclass
class Animation:
    frames: list = field(default_factory=list)
    speed: int = 0
    current_frame: int = 0

@dataclass
class Camera:
    x: int = 0
    y: int = 0