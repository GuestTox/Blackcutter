from enum import Enum
import pygame

class ResourceType(Enum):
    IMAGE = 1
    FONT = 2
    SOUND = 3

class ResourceManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.sounds = {}

    def load(self, type: ResourceType, id:str, filename: str, size=None, specialPath:bool=False):
        if specialPath:
            return pygame.image.load(f"{filename}").convert_alpha()
        
        if type == ResourceType.IMAGE:
            if self.images.get(id) is None:
                self.images[id] = pygame.image.load(f"/assets/images/{filename}").convert_alpha()
            return self.images[id]

        if type == ResourceType.FONT:
            if self.fonts.get(id) is None:
                self.fonts[id] = pygame.font.Font(f"assets/fonts/{filename}", size)
            return self.fonts[id]

        if type == ResourceType.SOUND:
            if self.sounds.get(id) is None:
                self.sounds[id] = pygame.mixer.Sound(f"assets/sounds/{filename}")
            return self.sounds[id]

    def delete(self, id):
        for dictionary in [self.images, self.fonts, self.sounds]:
            if id in dictionary:
                del dictionary[id]