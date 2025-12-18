
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class MadRiver(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Mad River, OH"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Mad River",
            server_url="https://www.skimadriver.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
    
    def _map_lift_type(self, lift):
        if lift['Type'] in ['quad']:
            return liftstatus.LiftType.CLF_4
        if lift['Type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['Type'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['Type'] in ['conveyor', 't-bar']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
