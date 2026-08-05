import esper, pygame
from components.dataclasses import Position, Animation, Camera
from dataclasses import dataclass, field
import components.utils as utils


@dataclass
class Renderable:
    image: pygame.Surface = field(default_factory=pygame.Surface)
    position: tuple = field(default_factory=tuple)


def handle_rendering(dt, screen):
    screen.fill((0, 0, 0))

    renderables = []
    try: 
        CameraID, cam = esper.get_component(Camera)[0]
    except IndexError:
        cam = Camera(0, 0)

    for _, (pos, anim) in esper.get_components(Position, Animation):
        new_x, new_y = pos.x - cam.x, pos.y - cam.y

        screen.blit(
            anim.frames[anim.current_frame],
            utils.centered(anim.frames[anim.current_frame], new_x, new_y)
    )

    pygame.display.flip()