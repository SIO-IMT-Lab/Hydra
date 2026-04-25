import time
from datetime import datetime, timezone
from typing import Any, Protocol
from dataclasses import dataclass


class SerializableMsg(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SerializableMsg": ...


@dataclass(slots=True)
class String:
    """
    Simple wrapper around a string for testing purposes.
    
    This is not intended for production use, but rather just to have a simple 
    message type for testing the system.
    """
    data: str

    def to_dict(self) -> dict[str, Any]:
        return { "data": self.data }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "String":
        return cls(data=data["data"])   


@dataclass(slots=True)
class Time:
    """
    Canonical time representation for the system.

    Stores time as Unix epoch nanoseconds (UTC).
    """
    ns: int

    def to_dict(self) -> dict[str, Any]:
        return {"ns": int(self.ns)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Time":
        return cls(ns=int(data["ns"]))

    @staticmethod
    def now() -> "Time":
        return Time(ns=time.time_ns())

    def to_seconds(self) -> float:
        return self.ns / 1e9

    def to_datetime_utc(self) -> datetime:
        return datetime.fromtimestamp(self.ns / 1e9, tz=timezone.utc)

    def __str__(self) -> str:
        # ISO Format: YYYY-MM-DDThh:mm:ss
        return self.to_datetime_utc().isoformat()


@dataclass(slots=True)
class SensorData:
    data: str
    timestamp: Time

    def to_dict(self) -> dict[str, Any]:
        return { "data": self.data, "timestamp": self.timestamp.to_dict() }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SensorData":
        return cls(data=data["data"], timestamp=Time.from_dict(data["timestamp"]))
    
     
@dataclass(slots=True)
class PDB_Command:
    pin_name: str
    new_state: bool # True for on, False for off

    def to_dict(self) -> dict[str, Any]:
        return { "pin_name": self.pin_name, "new_state": self.new_state }
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PDB_Command":
        return cls(pin_name=data["pin_name"], new_state=data["new_state"])

@dataclass(slots=True)
class PDB_State:
    voltages: dict[str, float]
    timestamp: Time

    def to_dict(self) -> dict[str, Any]:
        return {
            "voltages": self.voltages,
            "timestamp": self.timestamp.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PDB_State":
        return cls(
            voltages={str(k): float(v) for k, v in data["voltages"].items()},
            timestamp=Time.from_dict(data["timestamp"])
        )


MESSAGE_TYPE_REGISTRY = {
    "String": String,
    "Time": Time,
    "SensorData": SensorData,
    "PDB_Command": PDB_Command,
    "PDB_State": PDB_State,
}

def get_message_class(message_type: str):
    if message_type not in MESSAGE_TYPE_REGISTRY:
        # TODO: Replace with proper logging and custom exception
        raise ValueError(f"Message type '{message_type}' not found in registry.")
    return MESSAGE_TYPE_REGISTRY[message_type]

