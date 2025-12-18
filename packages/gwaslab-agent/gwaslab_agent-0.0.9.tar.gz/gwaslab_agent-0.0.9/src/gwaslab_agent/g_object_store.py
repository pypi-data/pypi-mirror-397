
class ObjectStore:
    def __init__(self):
        self.objects = {}

    def put(self, obj):
        obj_id = self.next_key()
        self.objects[obj_id] = obj
        return obj_id

    def get(self, obj_id):
        return self.objects[obj_id]

    def next_key(self):
        return f"subset_{len(self.objects)}"
