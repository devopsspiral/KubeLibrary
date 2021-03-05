

class BearerTokenWithPrefixException(Exception):

    def __init__(self):
        super().__init__("Unnecessary 'Bearer ' prefix in token")
    pass
