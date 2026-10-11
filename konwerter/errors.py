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