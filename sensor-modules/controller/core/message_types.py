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

    def to_iso(self) -> str:
        # ISO Format: YYYY-MM-DDThh:mm:ss.ssssss+00:00
        return self.to_datetime_utc().isoformat()
    
    def __str__(self) -> str:
        return self.to_iso()


@dataclass(slots=True)
class ConductivityData:
    timestamp: Time
    conductivity: float

    @classmethod
    def csv_fields(cls) -> list[str]:
        return ["timestamp", "conductivity"]

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.to_iso(),
            "conductivity": self.conductivity
        }
        
    def to_dict(self) -> dict[str, Any]:
        return { 
            "timestamp": self.timestamp.to_dict(), 
            "conductivity": self.conductivity 
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConductivityData":
        return cls(
            timestamp=Time.from_dict(data["timestamp"]),
            conductivity=data["conductivity"], 
        )


@dataclass(slots=True)
class APCData:
    timestamp: Time
    value_1: float
    value_2: float

    @classmethod
    def csv_fields(cls) -> list[str]:
        return ["timestamp", "value_1", "value_2"]

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.to_iso(),
            "value_1": self.value_1,
            "value_2": self.value_2,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.to_dict(),
            "value_1": self.value_1,
            "value_2": self.value_2,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "APCData":
        return cls(
            timestamp=Time.from_dict(data["timestamp"]),
            value_1=float(data["value_1"]),
            value_2=float(data["value_2"])
        )


@dataclass(slots=True)
class SITAData:
    timestamp: Time
    value_1: float
    value_2: float

    @classmethod
    def csv_fields(cls) -> list[str]:
        return [
            "timestamp",
            "value_1",
            "value_2",
        ]

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.to_iso(),
            "value_1": self.value_1,
            "value_2": self.value_2,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.to_dict(),
            "value_1": self.value_1,
            "value_2": self.value_2,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SITAData":
        return cls(
            timestamp=Time.from_dict(data["timestamp"]),
            value_1=float(data["value_1"]),
            value_2=float(data["value_2"]),
        )


@dataclass(slots=True)
class PDB_State:
    timestamp: Time
    voltages: dict[str, float]
    
    # Debating whether to hardcode the voltage fields here or just let it be dynamic. 
    # For now I'm hardcoding since we know the fields we want and it makes it easier 
    # to convert to CSV, but we can always change this later if we want more flexibility.
    VOLTAGE_FIELDS = ["A-IN", "RPi", "ETHR", "MOTH", "B-IN", "PANDA1", "CNDT", 
                      "APC", "C-IN", "PANDA2", "BUBBLE-CAM", "STARLINK"]
    
    @classmethod
    def csv_fields(cls) -> list[str]:
        return ["timestamp"] + cls.VOLTAGE_FIELDS

    def to_csv_row(self) -> dict[str, Any]:
        row = { "timestamp": self.timestamp.to_iso() }
        for field in self.VOLTAGE_FIELDS:
            row[field] = self.voltages.get(field)
        return row

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.to_dict(),
            "voltages": self.voltages
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PDB_State":
        return cls(
            timestamp=Time.from_dict(data["timestamp"]),
            voltages={str(k): float(v) for k, v in data["voltages"].items()}
        )


@dataclass(slots=True)
class PDB_ServiceRequest:
    correlation_id: str
    pin_name: str
    new_state: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "pin_name": self.pin_name,
            "new_state": self.new_state
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PDB_ServiceRequest":
        return cls(
            correlation_id=data["correlation_id"],
            pin_name=data["pin_name"],
            new_state=data["new_state"]
        )


@dataclass(slots=True)
class PDB_ServiceResponse:
    correlation_id: str
    success: bool
    actual_voltage: float
    pin_name: str
    error_message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "success": self.success,
            "actual_voltage": self.actual_voltage,
            "pin_name": self.pin_name,
            "error_message": self.error_message
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PDB_ServiceResponse":
        return cls(
            correlation_id=data["correlation_id"],
            success=data["success"],
            actual_voltage=data["actual_voltage"],
            pin_name=data["pin_name"],
            error_message=data["error_message"]
        )


MESSAGE_TYPE_REGISTRY = {
    "String": String,
    "Time": Time,
    "ConductivityData": ConductivityData,
    "APCData": APCData,
    "SITAData": SITAData,
    "PDB_State": PDB_State,
    "PDB_ServiceRequest": PDB_ServiceRequest,
    "PDB_ServiceResponse": PDB_ServiceResponse
}

def get_message_class(message_type: str):
    if message_type not in MESSAGE_TYPE_REGISTRY:
        raise ValueError(f"Message type '{message_type}' not found in registry")
    return MESSAGE_TYPE_REGISTRY[message_type]

