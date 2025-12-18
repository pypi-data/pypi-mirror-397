
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class LaurelMountain(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Laurel Mountain, PA"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Laurel Mountain",
            server_url="https://www.laurelmountainski.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
    
    def _map_lift_type(self, lift):
        if lift['Type'] in ['quad']:
            return liftstatus.LiftType.CLF_4
        if lift['Type'] in ['tow']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
