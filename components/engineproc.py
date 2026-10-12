import esper, pygame, math
from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT
from components.dataclasses import Position, Animation, Camera, PlayerTag, Velocity, Stickmanoid, BoxCollider
import components.utils as utils

class Rendering(esper.Processor):
    def __init__(self, screen, cameraEnt):
        super().__init__()
        self.cameraOnPlayer = False
        self.screen = screen
        self.cameraEnt = cameraEnt

    def process(self, **kwargs):
        self.screen.fill((0, 0, 0))

        if self.cameraOnPlayer:
            playerID, (cam, cam_pos, playertag) = esper.get_components(Camera, Position, PlayerTag)[0]
        else:
            camID, (cam, cam_pos) = esper.get_components(Camera, Position)[0]
        

        half_sw = self.screen.get_width() // 2
        half_sh = self.screen.get_height() // 2

        for _, (pos, anim) in esper.get_components(Position, Animation):
            # Center camera viewport on screen center
            new_x = (pos.x - cam_pos.x) + half_sw
            new_y = (pos.y - cam_pos.y) + half_sh

            draw_pos = (new_x, new_y) if anim.centering_exception else utils.centered(anim.frames[anim.current_frame], new_x, new_y)
            render_rect = anim.frames[anim.current_frame].get_rect(topleft=draw_pos)

            if render_rect.colliderect(self.screen.get_rect()):
                self.screen.blit(anim.frames[anim.current_frame], draw_pos)

        # Inside Rendering.process() loop:
        for _, (pos, stickmanoid) in esper.get_components(Position, Stickmanoid):
            if hasattr(stickmanoid, "computed_joints"):
                joints = stickmanoid.computed_joints
                
                # Apply camera offset to world coordinates
                def cam_offset(coord):
                    x = (coord[0] - cam_pos.x) + half_sw
                    y = (coord[1] - cam_pos.y) + half_sh
                    return (int(x), int(y))

                hip = cam_offset(joints["hip"])
                shoulder = cam_offset(joints["shoulder"])
                head = cam_offset(joints["head"])
                f1 = cam_offset(joints["foot1"])
                k1 = cam_offset(joints["knee1"])
                f2 = cam_offset(joints["foot2"])
                k2 = cam_offset(joints["knee2"])

                color = (255, 255, 255)
                thick = stickmanoid.limb_thickness

                # Draw Head
                pygame.draw.circle(self.screen, color, head, stickmanoid.head_radius, width=thick)
                # Draw Torso
                pygame.draw.line(self.screen, color, hip, shoulder, thick)
                # Draw Legs 1 (hip -> knee -> foot)
                pygame.draw.line(self.screen, color, hip, k1, thick)
                pygame.draw.line(self.screen, color, k1, f1, thick)
                # Draw Legs 2
                pygame.draw.line(self.screen, color, hip, k2, thick)
                pygame.draw.line(self.screen, color, k2, f2, thick)

        pygame.display.flip()

    def checkCameraOnPlayer(self):
        cameraOnPlayer = esper.get_components(Camera, PlayerTag)[0][1]
        if len(cameraOnPlayer) == 2:
            self.cameraEnt = cameraOnPlayer
            self.cameraOnPlayer = True
            print("camera on player")
            return True

class InputHandler(esper.Processor):
    def process(self, input, key_presses, **kwargs):
        _, (player_tag, velocity) = esper.get_components(PlayerTag, Velocity)[0]

        velocity.x = velocity.y = 0

        if key_presses[pygame.K_q]:
            velocity.x = 5
        if key_presses[pygame.K_d]:
            velocity.x = -5
        if key_presses[pygame.K_z]:
            velocity.y = 5
        if key_presses[pygame.K_s]:
            velocity.y = -5

class PhysicsProcessor(esper.Processor):
    def process(self, **kwargs):
        # 1. Move players/entities with velocity
        for _, (pos, vel, box) in esper.get_components(Position, Velocity, BoxCollider):
            # Create a rect for the moving entity
            entity_rect = pygame.Rect(pos.x, pos.y, box.width, box.height)

            # Horizontal movement & collision
            pos.x += vel.x
            entity_rect.x = pos.x
            
            for _, (c_pos, c_box) in esper.get_components(Position, BoxCollider):
                # Skip checking against itself if it's also a BoxCollider entity
                # (You can use tags like PlayerTag or filter out non-level colliders if needed)
                collider_rect = pygame.Rect(c_pos.x, c_pos.y, c_box.width, c_box.height)
                if entity_rect.colliderect(collider_rect):
                    if vel.x > 0:  # Moving right
                        pos.x = collider_rect.left - box.width
                    elif vel.x < 0:  # Moving left
                        pos.x = collider_rect.right
                    entity_rect.x = pos.x

            # Vertical movement & collision
            pos.y += vel.y
            entity_rect.y = pos.y
            
            for _, (c_pos, c_box) in esper.get_components(Position, BoxCollider):
                collider_rect = pygame.Rect(c_pos.x, c_pos.y, c_box.width, c_box.height)
                if entity_rect.colliderect(collider_rect):
                    if vel.y > 0:  # Moving down
                        pos.y = collider_rect.top - box.height
                    elif vel.y < 0:  # Moving up
                        pos.y = collider_rect.bottom
                    entity_rect.y = pos.y

class StickmanoidIKProcessor(esper.Processor):
    def __init__(self):
        super().__init__()
        self.timer = 0

    def process(self, dt, **kwargs):
        self.timer += dt * 5  # Animation cycle timer

        for _, (velocity, pos, stickmanoid) in esper.get_components(Velocity, Position, Stickmanoid):
            # 1. Determine facing direction based on movement
            if velocity.x != 0:
                stickmanoid.facing_direction = 1 if velocity.x > 0 else -1

            # 2. Base positions (hips and shoulders)
            hip_x, hip_y = pos.x, pos.y - stickmanoid.torso_length // 2
            
            # Torso orientation vector
            torso_angle = -math.pi / 2  # pointing straight up
            shoulder_x = hip_x + math.cos(torso_angle + math.pi/2) * stickmanoid.torso_length * 0.2 * stickmanoid.facing_direction
            shoulder_y = hip_y + math.sin(torso_angle) * stickmanoid.torso_length

            # 3. Simple procedural leg targets (Walking cycle simulation)
            is_moving = math.hypot(velocity.x, velocity.y) > 0.1
            stride = 25 if is_moving else 0
            
            # Leg targets using a sine wave cycle
            foot1_target_x = hip_x + math.sin(self.timer) * stride
            foot1_target_y = hip_y + stickmanoid.leg_length + stickmanoid.foreleg_length
            
            foot2_target_x = hip_x + math.sin(self.timer + math.pi) * stride
            foot2_target_y = hip_y + stickmanoid.leg_length + stickmanoid.foreleg_length

            # 4. Solve 2-bone IK for legs
            # Knee bend direction: 1 or -1
            knee1 = utils.solve_2bone_ik(hip_x, hip_y, foot1_target_x, foot1_target_y, 
                                         stickmanoid.leg_length, stickmanoid.foreleg_length, bend_dir=1)
            knee2 = utils.solve_2bone_ik(hip_x, hip_y, foot2_target_x, foot2_target_y, 
                                         stickmanoid.leg_length, stickmanoid.foreleg_length, bend_dir=1)

            # Store computed joint positions directly onto the component or entity for drawing
            stickmanoid.computed_joints = {
                "hip": (hip_x, hip_y),
                "shoulder": (shoulder_x, shoulder_y),
                "head": (shoulder_x, shoulder_y - stickmanoid.head_radius - 5),
                "foot1": (foot1_target_x, foot1_target_y),
                "knee1": knee1,
                "foot2": (foot2_target_x, foot2_target_y),
                "knee2": knee2
            }