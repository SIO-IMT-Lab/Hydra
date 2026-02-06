from typing import Any, Protocol
from dataclasses import dataclass

class SerializableMsg(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SerializableMsg": ...


@dataclass(slots=True)
class String:
    data: str

    def to_dict(self) -> dict[str, Any]:
        return { "data": self.data }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "String":
        return cls(data=data["data"])   
