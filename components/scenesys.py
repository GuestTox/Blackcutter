from dataclasses import dataclass, field
import components.dataclasses as Components
from typing import List, Dict, Any
from components.res_mngr import *
import json, pygame, esper

class Scene:
    def __init__(self):
        self.colliders = []
        self.areas = []
        self.entities = []
        self.id = None

    def fetch_data(self, id):
        self.id = id

        with open(f"./assets/levels/{id}.json") as file:
            data = json.load(file)

        self.colliders = data["colliders"]
        self.areas = data["areas"]
        self.entities = data["entities"]

    def load_scene(self, resmanager: ResourceManager, target_screen_size: tuple[int, int] = (1000, 800)):
        raw_bg = resmanager.load(ResourceType.IMAGE, "background", f"assets/levels/{self.id}.png", specialPath=True)
        
        # Calculate aspect ratio scaling
        bg_w, bg_h = raw_bg.get_width(), raw_bg.get_height()
        screen_w, screen_h = target_screen_size

        # Fit scale (covers screen height or width while keeping proportions)
        scale_factor = max(screen_w / bg_w, screen_h / bg_h)
        new_size = (int(bg_w * scale_factor), int(bg_h * scale_factor))

        # Smoothly scale the background surface
        self.background = pygame.transform.smoothscale(raw_bg, new_size)

        player_entity = next((entity for entity in self.entities if entity["entity_id"] == 1), None)
        if player_entity:
            self.player_position = (player_entity.get("x", 0), player_entity.get("y", 0))
        else:
            self.player_position = (0, 0)

        return SceneData(
            player_pos=self.player_position,
            background_image=self.background,
            colliders=self.colliders,
            areas=self.areas,
            entities=self.entities
        )

@dataclass
class SceneData:
    player_pos: tuple[int, int] = (0, 0)
    background_image: pygame.Surface = None
    colliders: List[Dict[str, Any]] = field(default_factory=list)
    areas: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)

class SceneManager:
    def __init__(self, scene:SceneData):
        self.currentScene = scene

    def on_load(self):
        esper.create_entity(
            Components.Position(0, 0),
            Components.Animation([self.currentScene.background_image])
        )

        # player_texture = pygame.Surface((30, 30), pygame.SRCALPHA)
        # pygame.draw.circle(player_texture, (255, 0, 0), (15, 15), 15)

        # esper.create_entity(
        #     Components.Position(self.currentScene.player_pos[0], self.currentScene.player_pos[1]),
        #     Components.Animation([player_texture]),
        #     Components.PlayerTag(),
        #     Components.BoxCollider(30, 30),
        #     Components.Camera()
        # )

        esper.create_entity(
                            Components.Position(self.currentScene.player_pos[0], self.currentScene.player_pos[1]),
                            Components.PlayerTag(),
                            Components.BoxCollider(30, 30),
                            Components.Velocity(0,0),
                            Components.Camera(),
                            Components.Stickmanoid(
                                limb_thickness=10,
                                arm_length=20,
                                forearm_length=20,
                                leg_length=25,
                                foreleg_length=25,
                                torso_length=40,
                                head_radius=20
                            )
                        )

        # Spawn level colliders from scene data
        for collider in self.currentScene.colliders:
            esper.create_entity(
                Components.Position(int(collider["x"]), int(collider["y"])),
                Components.BoxCollider(
                    width=int(collider["w"]),
                    height=int(collider["h"]),
                    rotation=int(collider.get("rot", 0))
                )
            )