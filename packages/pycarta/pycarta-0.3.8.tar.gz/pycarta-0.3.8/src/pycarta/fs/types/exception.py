from pycarta.fs.types.file import CartaFsFile


class FileUnavailableException(Exception):
    """File is in a state where it cannot be reliably retrieved or modified"""

    def __init__(self, message: str = None, file: CartaFsFile = None):
        super().__init__(message)
        self.file = file
