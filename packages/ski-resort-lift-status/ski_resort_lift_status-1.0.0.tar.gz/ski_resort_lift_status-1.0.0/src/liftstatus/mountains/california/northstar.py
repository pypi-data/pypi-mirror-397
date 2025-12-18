
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class Northstar(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Northstar, CA"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Northstar",
            server_url="https://www.northstarcalifornia.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx",
            timezone=pytz.timezone('US/Pacific'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['Type'] in ['six']:
            return liftstatus.LiftType.CLD_6
        if lift['Type'] in ['quad']:
            if "Express" in lift['Name']:
                return liftstatus.LiftType.CLD_4
            else:
                return liftstatus.LiftType.CLF_4
        if lift['Type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['Type'] in ['conveyor', 't-bar']:
            return liftstatus.LiftType.SL
        if lift['Type'] in ['gondola']:
            return liftstatus.LiftType.MGD

        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
