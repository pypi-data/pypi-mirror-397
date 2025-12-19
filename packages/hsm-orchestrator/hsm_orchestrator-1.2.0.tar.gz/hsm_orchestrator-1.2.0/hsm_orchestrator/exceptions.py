class WrongSystem(Exception):
    """Exception raised if the script is run on the offline HSM

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RepoNotReady(Exception):
    """Exception raised if there is a problem with the offline HSM git repo

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
