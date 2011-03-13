class CampError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        repr(self.value)


