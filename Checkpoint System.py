class MicrotonECheckpoint:
    def __init__(self):
        self.checkpoints = []

    def save_checkpoint(self, state):
        self.checkpoints.append(state)

    def load_checkpoint(self, index):
        if index < len(self.checkpoints):
            return self.checkpoints[index]
        return None
