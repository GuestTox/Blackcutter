import math

def centered(surf, x, y):
    w = surf.get_width()
    h = surf.get_height()

    new_x = x - w / 2
    new_y = y - h / 2

    return new_x, new_y

def solve_2bone_ik(root_x, root_y, target_x, target_y, l1, l2, bend_dir=1):
    """
    Solves 2-bone IK and returns the intermediate joint position (x, y).
    bend_dir: 1 or -1 to control which way the joint bends (e.g., knees bend forward/back).
    """
    dx = target_x - root_x
    dy = target_y - root_y
    distance = math.hypot(dx, dy)
    
    # Clamp distance if target is out of reach
    max_reach = l1 + l2
    if distance > max_reach:
        distance = max_reach - 0.0001
        # Scale target back to max reach
        angle_to_target = math.atan2(dy, dx)
        target_x = root_x + math.cos(angle_to_target) * distance
        target_y = root_y + math.sin(angle_to_target) * distance
        dx = target_x - root_x
        dy = target_y - root_y

    # Clamp distance if target is too close (folding inside)
    min_reach = abs(l1 - l2)
    if distance < min_reach:
        distance = min_reach + 0.0001

    # Law of cosines to find joint angle
    cosine_angle = (l1**2 + distance**2 - l2**2) / (2 * l1 * distance)
    cosine_angle = max(-1.0, min(1.0, cosine_angle)) # Clamp for safety
    angle_offset = math.acos(cosine_angle)
    
    base_angle = math.atan2(dy, dx)
    joint_angle = base_angle + (bend_dir * angle_offset)
    
    joint_x = root_x + math.cos(joint_angle) * l1
    joint_y = root_y + math.sin(joint_angle) * l1
    
    return (joint_x, joint_y)