import hashlib

class MicrotonEHashwords:
    def __init__(self):
        self.keys = {}
        self.locks = {}

    def generate_key(self, identifier):
        key = hashlib.sha256(identifier.encode()).hexdigest()
        self.keys[identifier] = key
        return key

    def generate_lock(self, identifier):
        lock = hashlib.sha256(identifier.encode()).hexdigest()
        self.locks[identifier] = lock
        return lock
