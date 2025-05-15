class Task:
    def __init__(self, title, description, buyer, price=10, status='open'):
        self.title = title
        self.description = description
        self.buyer = buyer
        self.price = price
        self.status = status

    def to_dict(self):
        return self.__dict__

