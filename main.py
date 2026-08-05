import pygame, esper
import components.engineproc as Engineproc
import components.dataclasses as Dataclasses
import components.scenesys as SceneSystem
from pathlib import Path

GAME_FOLDER = str(Path(__file__).resolve().parent)

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((1000, 800))

        esper.add_processor(Engineproc.handle_rendering)

    def run(self, running):
        while running:
            dt = self.clock.tick(60) / 1000
            esper.process(dt, self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.render()

        pygame.quit()

if __name__ == "__main__":
    game = Game(True)
    game.run(True)