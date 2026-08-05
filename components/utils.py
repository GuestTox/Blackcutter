def centered(surf, x, y):
    w = surf.get_width()
    h = surf.get_height()

    new_x = x - w / 2
    new_y = y - h / 2

    return new_x, new_y