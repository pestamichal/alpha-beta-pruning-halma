class TreeNode:
    def __init__(self, game_state, player_to_move=None, parent=None):
        self.game_state = game_state  # Represents the current game state (2D list)
        self.player_to_move = player_to_move  # Player to make a move in this state
        self.children: [TreeNode] = []  # List to store child nodes
        self.parent = parent
        self.value = None

    def add_child(self, child_node):
        self.children.append(child_node)

    def is_leaf(self):
        return len(self.children) == 0

    def __str__(self):
        return f'Player {self.player_to_move}: {self.value} {self.game_state}'

    def __repr__(self):
        return f"Player {self.player_to_move}: {self.game_state}"