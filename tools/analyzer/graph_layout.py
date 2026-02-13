import math

def radial_layout(nodes):
    positions = {}
    r = 200
    step = 2 * math.pi / max(len(nodes), 1)

    for i, n in enumerate(sorted(nodes)):
        angle = i * step
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        positions[n] = (x, y)

    return positions
