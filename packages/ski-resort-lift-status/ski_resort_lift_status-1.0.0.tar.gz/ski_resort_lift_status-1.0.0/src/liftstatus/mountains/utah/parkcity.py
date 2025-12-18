
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class ParkCity(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Park City, UT"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Park City",
            server_url="https://www.parkcitymountain.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['Type'] in ['six']:
            return liftstatus.LiftType.CLD_6
        if lift['Type'] in ['quad', 'combination']:
            if lift['Name'] in ['Dreamcatcher', 'Dreamscape', 'Over and Out', 'Peak 5', 'Timberline']:
                return liftstatus.LiftType.CLF_4
            else:
                return liftstatus.LiftType.CLD_4
        if lift['Type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['Type'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['Type'] in ['conveyor', 't-bar']:
            return liftstatus.LiftType.SL
        if lift['Type'] in ['gondola']:
            if lift['Name'] in 'Cabriolet':
                return liftstatus.LiftType.CABRIO
            else:
                return liftstatus.LiftType.MGD
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
