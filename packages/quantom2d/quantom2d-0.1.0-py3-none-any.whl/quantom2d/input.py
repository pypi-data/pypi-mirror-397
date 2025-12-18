class Input:
    _keys = set()

    @staticmethod
    def key_down(event):
        Input._keys.add(event.keysym)

    @staticmethod
    def key_up(event):
        Input._keys.discard(event.keysym)

    @staticmethod
    def is_down(key):
        return key in Input._keys
