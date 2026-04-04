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
    
     
# @dataclass(slots=True)
# class PDB_Command:
#     pin: str
#     state: bool
#     request_id: Optional[str] = None
#
#     def to_dict(self) -> dict[str, Any]:
#         return {
#             "pin": self.pin,
#             "state": self.state,
#             "request_id": self.request_id,
#         }
#
#     @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "PDB_Command":
#         return cls(
#             pin=data["pin"],
#             state=data.get("state"),
#             request_id=data.get("request_id"),
#         )
#
# @dataclass(slots=True)
# class PDB_State:
#     voltages: list[float]
#     pins: list[bool]
#     stamp_ns: int
#
#     def to_dict(self) -> dict[str, Any]:
#         return {
#             "voltages": self.voltages,
#             "pins": self.b_pins,
#             "stamp_ns": int(self.stamp_ns),
#         }
#
#     @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "PdbStatus":
#         return cls(
#             voltages=[float(x) for x in data["voltages"]],
#             pins=[bool(x) for x in data["pins"]],
#             stamp_ns=int(data["stamp_ns"]),
#         )
#
#
MESSAGE_TYPE_REGISTRY = {
    "String": String,
    "Time": Time,
    "SensorData": SensorData,
}

def get_message_class(message_type: str):
    return MESSAGE_TYPE_REGISTRY.get(message_type, String)

