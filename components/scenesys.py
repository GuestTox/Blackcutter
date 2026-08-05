import esper, pygame, json
from components.dataclasses import Position, Animation, Camera
from dataclasses import dataclass, field
import components.utils as utils
from pathlib import Path

GAME_FOLDER = str(Path(__file__).resolve().parent)

class Scene:
    def __init__(self, game):
        self.game = game

    def load_data(self, id):
        with json.load(f"{GAME_FOLDER}//assets/scenes.json") as f:
            file = dict(f)
            file.get(self.id)