
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
import datetime
import sys

try:
    from ._version import version as __version__
except ImportError:
    __version__ = 'unknown'

_USER_AGENT = f"ski-resort-lift-status/{__version__} (+https://github.com/NietoSkunk/ski-resort-lift-status)"

class LiftType(StrEnum):
    """Enumeration of supported type codes for a lift.

    These follow the format listed at https://cable.blog.hu/2017/10/15/type_guide.
    """

    CLD_3   = 'Detachable Triple'
    CLD_4   = 'Detachable Quad'
    CLD_6   = 'Detachable Six-Pack'
    CLD_8   = 'Detachable Eight-Pack'
    CLF_1   = 'Fixed Grip Single'
    CLF_2   = 'Fixed Grip Double'
    CLF_3   = 'Fixed Grip Triple'
    CLF_4   = 'Fixed Grip Quad'
    CLF_6   = 'Fixed Grip Six-Pack'
    SL      = 'Surface Lift'
    MGD     = 'Gondola'
    BGD     = 'Bicable Gondola'
    TGD     = 'Tricable Gondola'
    CGD     = 'Chondola'
    CABRIO  = 'Cabriolet'
    FUT     = 'Funitel'
    ATW     = 'Aerial Tramway'
    FUN     = 'Funicular'

    UNKNOWN = 'LiftTypeUnknown'


class LiftStatus(StrEnum):
    """Enumeration of lift status options.
    
    The interpretation of each type varies between different mountains.
    For example, one mountain may used CLOSED to represent a lift that has not yet opened
    for the day, while another may use it to represent one that is closed for the season,
    and another may use it to represent one that is closed to the public. 
    """

    CLOSED      = 'Closed'
    OPEN        = 'Open'
    HOLD        = 'On Hold'
    DELAYED     = 'Delayed'
    SCHEDULED   = 'Scheduled'
    RESTRICTED  = 'Restricted'

    UNKNOWN     = 'LiftStatusUnknown'


@dataclass
class Lift:
    name: str
    type: LiftType
    status: LiftStatus
    updated_at: datetime.datetime | None = None
    open_time: datetime.time | None = None
    closed_time: datetime.time | None = None
    wait_time: datetime.timedelta | None = None

    def __str__(self) -> str:
        ret_str = f"Lift<name='{self.name}', type={self.type}, status={self.status}"
        if self.updated_at is not None:
            ret_str += f", updated_at={self.updated_at.strftime('%Y-%m-%dT%H:%M:%S%z')}"
        if self.open_time is not None:
            ret_str += f", open_time={self.open_time.strftime('%I:%M%p')}"
        if self.closed_time is not None:
            ret_str += f", closed_time={self.closed_time.strftime('%I:%M%p')}"
        if self.wait_time is not None:
            ret_str += f", wait_time={self.wait_time}"
        ret_str += '>'
        return ret_str

class Mountain(ABC):

    def __init__(self, name: str):
        self._name = name

    def __str__(self) -> str:
        return f"Mountain<name='{self._name}'>"

    @abstractmethod
    def get_lift_status() -> list[Lift]:
        pass


# Excluding APIs and _USER_AGENT from `import *`, since they're not 
# meant to be directly used, and should be explicitly imported if needed.
__all__ = ['LiftType', 'LiftStatus', 'Lift', 'Mountain', 'mountains', 'exceptions']

def __getattr__(name):
    import importlib

    if name in __all__:
        return importlib.import_module("." + name, __name__)
    raise AttributeError(
        "module {!r} has not attribute {!r}".format(__name__, name)
    )

def __dir__():
    # __dir__ should include all the lazy-importable modules as well.
    return [x for x in globals() if x not in sys.modules] + __all__
