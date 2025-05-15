class User:
    def __init__(self, username, email, role):
        self.username = username
        self.email = email
        self.role = role

    def to_dict(self):
        return self.__dict__

