"""Własne wyjątki konwertera.

Wszystkie dziedziczą po ConversionError, dzięki czemu GUI może rozpoznać rodzaj
problemu i pokazać użytkownikowi odpowiedni, czytelny komunikat.
"""


class ConversionError(Exception):
    """Bazowa klasa błędów konwersji - przechowuje komunikat dla użytkownika."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CorruptedInputFile(ConversionError):
    """Plik wejściowy jest uszkodzony, ma złe kodowanie lub nie jest danym formatem."""
    pass

class UnidentifiedDelimiter(ConversionError):
    """Nie udało się rozpoznać separatora w pliku CSV."""
    pass

class EmptyInputFile(ConversionError):
    """Plik wejściowy nie zawiera żadnych danych do konwersji."""
    pass

class JsonIsNested(ConversionError):
    """JSON zawiera zagnieżdżone obiekty/listy, których nie da się zapisać jako CSV."""
    pass

class InvalidJsonStructure(ConversionError):
    """JSON nie jest obiektem ani listą obiektów (np. [1, 2, 3])."""
    pass


class TargetExists(ConversionError):
    """Plik docelowy już istnieje, a nadpisanie nie zostało potwierdzone."""
    def __init__(self, path):
        # zapamiętujemy ścieżkę, żeby GUI mogło ją pokazać w pytaniu o nadpisanie
        self.path = path
        super().__init__(f"Plik docelowy już istnieje: {path}")
