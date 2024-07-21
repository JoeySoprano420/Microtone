import pickle

class MicrotonECheckpointSystem:
    def __init__(self, filename):
        self.filename = filename

    def save_checkpoint(self, state):
        with open(self.filename, 'wb') as f:
            pickle.dump(state, f)

    def load_checkpoint(self):
        with open(self.filename, 'rb') as f:
            return pickle.load(f)
