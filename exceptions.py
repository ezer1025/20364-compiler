class CPLException(Exception):
    def __init__(self, message, line_number):
        self.message = message
        self.line_number = line_number