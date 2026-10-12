import pygame, esper
import components.engineproc as Engineproc
import components.dataclasses as Dataclasses
import components.scenesys as SceneSystem
import components.res_mngr as ResourceSys
from pathlib import Path

GAME_FOLDER = str(Path(__file__).resolve().parent)

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((1600, 900))
        self.resource_manager = ResourceSys.ResourceManager()

        pygame.display.set_caption("Blackcutter")
        self.default_camera = esper.create_entity(
            Dataclasses.Camera(1),
            Dataclasses.Position(0, 0)
        )

        renderingprocessor = Engineproc.Rendering(self.screen, self.default_camera)
        esper.add_processor(renderingprocessor)

        inputprocessor = Engineproc.InputHandler()
        esper.add_processor(inputprocessor)
        
        ikstickmanprocessor = Engineproc.StickmanoidIKProcessor()
        esper.add_processor(ikstickmanprocessor)

        physicsproc = Engineproc.PhysicsProcessor()
        esper.add_processor(physicsproc)

        self.SceneLoading()
        renderingprocessor.checkCameraOnPlayer()

    def SceneLoading(self):
        main_scene = SceneSystem.Scene()
        main_scene.fetch_data("test01")
        main_scene = main_scene.load_scene(self.resource_manager)
        
        scene_manager = SceneSystem.SceneManager(main_scene)
        scene_manager.on_load()

    def run(self, running):
        while running:
            dt = self.clock.tick(60) / 1000
            game_events = pygame.event.get()
            pressed_keys = pygame.key.get_pressed()

            for event in game_events:
                if event.type == pygame.QUIT:
                    running = False

            esper.process(dt=dt, input=game_events, key_presses=pressed_keys)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run(True)