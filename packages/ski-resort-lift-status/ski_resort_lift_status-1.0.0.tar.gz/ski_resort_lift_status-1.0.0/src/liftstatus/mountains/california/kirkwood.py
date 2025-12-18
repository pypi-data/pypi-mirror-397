
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class Kirkwood(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Kirkwood, CA"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Kirkwood",
            server_url="https://www.kirkwood.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx",
            timezone=pytz.timezone('US/Pacific'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['Type'] in ['quad']:
            if "Express" in lift['Name']:
                return liftstatus.LiftType.CLD_4
            else:
                return liftstatus.LiftType.CLF_4
        if lift['Type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['Type'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['Type'] in ['conveyor', 't-bar', 'tow']:
            return liftstatus.LiftType.SL

        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
