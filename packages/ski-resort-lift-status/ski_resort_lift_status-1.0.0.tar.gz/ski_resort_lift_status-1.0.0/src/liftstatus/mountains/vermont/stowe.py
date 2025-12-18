
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class Stowe(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Stowe, VT"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Stowe",
            server_url="https://www.stowe.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['Type'] in ['six']:
            return liftstatus.LiftType.CLD_6
        if lift['Type'] in ['quad']:
            if lift['Name'] in ['Meadows Quad']:
                return liftstatus.LiftType.CLF_4
            else:
                return liftstatus.LiftType.CLD_4
        if lift['Type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['Type'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['Type'] in ['conveyor']:
            return liftstatus.LiftType.SL
        if lift['Type'] in ['gondola']:
            return liftstatus.LiftType.MGD
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
