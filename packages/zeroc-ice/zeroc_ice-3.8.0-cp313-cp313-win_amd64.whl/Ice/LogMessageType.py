# Copyright (c) ZeroC, Inc.

# slice2py version 3.8.0

from __future__ import annotations
import IcePy

from enum import Enum

class LogMessageType(Enum):
    """
    Represents the different types of log messages.
    
    Enumerators:
    
    - PrintMessage:
        The :class:`Ice.RemoteLoggerPrx` received a print message.
    
    - TraceMessage:
        The :class:`Ice.RemoteLoggerPrx` received a trace message.
    
    - WarningMessage:
        The :class:`Ice.RemoteLoggerPrx` received a warning message.
    
    - ErrorMessage:
        The :class:`Ice.RemoteLoggerPrx` received an error message.
    
    Notes
    -----
        The Slice compiler generated this enum class from Slice enumeration ``::Ice::LogMessageType``.
    """
    
    PrintMessage = 0
    TraceMessage = 1
    WarningMessage = 2
    ErrorMessage = 3

_Ice_LogMessageType_t = IcePy.defineEnum(
    "::Ice::LogMessageType",
    LogMessageType,
    (),
    {
        0: LogMessageType.PrintMessage,
        1: LogMessageType.TraceMessage,
        2: LogMessageType.WarningMessage,
        3: LogMessageType.ErrorMessage,
    }
)

__all__ = ["LogMessageType", "_Ice_LogMessageType_t"]
