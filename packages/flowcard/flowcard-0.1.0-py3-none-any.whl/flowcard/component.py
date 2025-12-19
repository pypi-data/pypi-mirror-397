# Standard Library
from abc import ABC, abstractmethod
from typing import Any # Changed from typing import Dict


class Component(ABC):
    name: str # Changed: name is now a class variable annotation

    def __init__(self) -> None:
        pass

    @abstractmethod
    def to_html(self) -> dict[str, str]: # Changed: Specific return type
        pass

    @abstractmethod
    def to_markdown(self) -> str: # Changed: Specific return type
        pass


class Container(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def to_html(self):
        pass

    @abstractmethod
    def to_markdown(self):
        pass
