class BearerTokenWithPrefixException(Exception):

    ROBOT_SUPPRESS_NAME = True

    def __init__(self):
        super().__init__("Unnecessary 'Bearer ' prefix in token")
    pass
