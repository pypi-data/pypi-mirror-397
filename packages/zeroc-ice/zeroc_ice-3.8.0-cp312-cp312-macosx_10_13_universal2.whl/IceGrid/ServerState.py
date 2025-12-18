# Copyright (c) ZeroC, Inc.

# slice2py version 3.8.0

from __future__ import annotations
import IcePy

from enum import Enum

class ServerState(Enum):
    """
    Represents the state of a server.
    
    Enumerators:
    
    - Inactive:
        The server is not running.
    
    - Activating:
        The server is being activated and will change to the active state when the registered server object adapters
        are activated or to the activation timed out state if the activation timeout expires.
    
    - ActivationTimedOut:
        The server activation timed out.
    
    - Active:
        The server is running.
    
    - Deactivating:
        The server is being deactivated.
    
    - Destroying:
        The server is being destroyed.
    
    - Destroyed:
        The server is destroyed.
    
    Notes
    -----
        The Slice compiler generated this enum class from Slice enumeration ``::IceGrid::ServerState``.
    """
    
    Inactive = 0
    Activating = 1
    ActivationTimedOut = 2
    Active = 3
    Deactivating = 4
    Destroying = 5
    Destroyed = 6

_IceGrid_ServerState_t = IcePy.defineEnum(
    "::IceGrid::ServerState",
    ServerState,
    (),
    {
        0: ServerState.Inactive,
        1: ServerState.Activating,
        2: ServerState.ActivationTimedOut,
        3: ServerState.Active,
        4: ServerState.Deactivating,
        5: ServerState.Destroying,
        6: ServerState.Destroyed,
    }
)

__all__ = ["ServerState", "_IceGrid_ServerState_t"]
