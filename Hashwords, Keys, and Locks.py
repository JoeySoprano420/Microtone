class HashwordManager:
    def __init__(self):
        self.hashwords = {}
        self.keys = {}
        self.locks = {}

    def add_hashword(self, hashword, value):
        self.hashwords[hashword] = value

    def get_hashword(self, hashword):
        return self.hashwords.get(hashword, None)

    def add_key(self, key, lock):
        self.keys[key] = lock

    def unlock(self, key):
        lock = self.keys.get(key, None)
        if lock and lock in self.locks:
            return self.locks[lock]
        return None
