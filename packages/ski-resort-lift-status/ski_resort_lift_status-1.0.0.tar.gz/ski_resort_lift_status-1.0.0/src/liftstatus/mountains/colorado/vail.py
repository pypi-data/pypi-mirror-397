
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class Vail(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Vail, CO"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Vail",
            server_url="https://www.vail.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )
    
    def _map_lift_name(self, lift):
        if '#' in lift['Name']:
            split_name = lift['Name'].split('#')
            return f"#{split_name[1].strip()} {split_name[0].strip()}"
        return super()._map_lift_name(lift)

    def _map_lift_type(self, lift):
        if lift['Type'] in ['six']:
            return liftstatus.LiftType.CLD_6
        if lift['Type'] in ['triple'] or lift['Name'] in ['Gopher Hill #12']: # Why is this reported as quad?
            return liftstatus.LiftType.CLF_3
        if lift['Type'] in ['quad']:
            if lift['Name'] in ['Cascade Village #20']:
                return liftstatus.LiftType.CLF_4
            else:
                return liftstatus.LiftType.CLD_4
        if lift['Type'] in ['conveyor', 't-bar']:
            return liftstatus.LiftType.SL
        if lift['Type'] in ['gondola']:
            return liftstatus.LiftType.MGD
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
