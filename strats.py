
def euclidean_dist(pos, base):
    return 30 - ((pos[0] - base[0])**2 + (pos[1] - base[1])**2)**0.5
def manhattan_dist(pos, base):
    return 30 - (abs(pos[0] - base[0]) + abs(pos[1] - base[1]))

def chebyshev_dist(pos, base):
    return 30 - max(abs(pos[0] - base[0]), abs(pos[1] - base[1]))