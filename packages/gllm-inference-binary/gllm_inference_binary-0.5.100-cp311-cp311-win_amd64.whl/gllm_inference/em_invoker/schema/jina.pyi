from enum import StrEnum

class InputType(StrEnum):
    """Defines the supported input types for the Jina AI embedding API."""
    IMAGE_URL: str
    TEXT: str

class Key(StrEnum):
    """Defines key constants used in the Jina AI API payloads."""
    DATA: str
    EMBEDDING: str
    EMBEDDINGS: str
    ERROR: str
    IMAGE_URL: str
    INPUT: str
    JSON: str
    MESSAGE: str
    MODEL: str
    RESPONSE: str
    STATUS: str
    TASK: str
    TEXT: str
    TYPE: str
    URL: str

class OutputType(StrEnum):
    """Defines the expected output types returned by the Jina AI embedding API."""
    DATA: str
    EMBEDDING: str
