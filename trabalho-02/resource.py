class Resource():
    def __init__(self, name):
        self.name = name
        self.state = 'unrequested'
        self.req_timestamp = 0
        self.n_ok = 0
        self.next_queue = []

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name