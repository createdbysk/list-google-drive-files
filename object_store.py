class ObjectStore(object):
    def __init__(self):
        self.store = {}

    @classmethod
    def create(cls):
        return cls()

    def add_object(self, name, object, account):
        if name not in self.store:
            self.store[name] = []

        self.store[name].append((account, object))

    def find_object(self, name):
        object_to_return = self.store.get(name, [])
        return object_to_return

    def json_dumps(self):
        import json
        json_string = json.dumps(self.store, indent=4)
        return json_string

    def __iter__(self):
        return self.store.__iter__()