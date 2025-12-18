
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class BeaverCreek(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Beaver Creek, CO"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Beaver Creek",
            server_url="https://www.beavercreek.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['Type'] in ['']:
            if lift['Name'] in ['Centennial Express: Chair 6']:
                # BC reports the chondola as two separate lifts
                return liftstatus.LiftType.CLD_6
            else:
                raise liftstatus.exceptions.APIParseException(f"Empty Type value for lift {lift['Name']}")
        if lift['Type'] in ['quad']:
            if lift['Name'] in ['Reunion']:
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
