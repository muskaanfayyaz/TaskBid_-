class Bid:
    def __init__(self, task, seller, message):
        self.task = task
        self.seller = seller
        self.message = message

    def to_dict(self):
        return self.__dict__
