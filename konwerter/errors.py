class ConversionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CorruptedInputFile(ConversionError):
    pass

class UnidentifiedDelimiter(ConversionError):
    pass

class EmptyInputFile(ConversionError):
    pass

class JsonIsNested(ConversionError):
    pass

class InvalidJsonStructure(ConversionError):
    """JSON nie jest obiektem ani listą obiektów (np. [1, 2, 3])."""
    pass


class TargetExists(ConversionError):
    """Plik docelowy już istnieje, a nadpisanie nie zostało potwierdzone."""
    def __init__(self, path):
        self.path = path
        super().__init__(f"Plik docelowy już istnieje: {path}")
