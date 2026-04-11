from enum import Enum


class SITA_COMMANDS(Enum):
    POWER_UP = b"\r\n:020605000100F2\r\n"
    NO_CAL = b"\r\n:020601000600F1\r\n"
    SAMPLE = b"\r\n:020601000B00EC\r\n"
    QUERY = b"\r\n:020618000500DB\r\n"
    POWER_OFF = b"\r\n:020605000000F3\r\n"
    STOP = b"\r\n:020618000000E0\r\n"