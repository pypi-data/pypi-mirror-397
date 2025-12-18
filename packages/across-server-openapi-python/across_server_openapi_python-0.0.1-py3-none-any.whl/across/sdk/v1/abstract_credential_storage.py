from abc import ABC, abstractmethod


class CredentialStorage(ABC):
    @property
    @abstractmethod
    def days_before_exp(self) -> int: ...

    @abstractmethod
    def id(self, force: bool = False) -> str: ...

    @abstractmethod
    def secret(self, force: bool = False) -> str: ...

    @abstractmethod
    def update_key(self, key: str) -> None: ...
