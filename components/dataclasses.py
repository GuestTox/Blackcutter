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
class Acceleration:
    x: int = 0
    y: int = 0
    mass: int = 1

@dataclass
class Animation:
    frames: list = field(default_factory=list)
    speed: int = 0
    current_frame: int = 0
    layer: int = 0
    centering_exception: bool = False

@dataclass
class BoxCollider:
    width: int
    height: int
    rotation: int = 0

@dataclass
class Stickmanoid:
    limb_thickness: int
    arm_length: int
    forearm_length: int
    leg_length: int
    foreleg_length: int
    torso_length: int
    head_radius: int
    facing_direction: int = 1  # 1 for right, -1 for left

#######################################
#                TAGS
#######################################

@dataclass
class PlayerTag: pass

@dataclass
class Camera:
    zoom: float = 1.0