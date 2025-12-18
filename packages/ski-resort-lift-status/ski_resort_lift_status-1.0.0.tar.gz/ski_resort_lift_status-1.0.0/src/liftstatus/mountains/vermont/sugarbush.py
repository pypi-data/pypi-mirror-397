
import liftstatus
import liftstatus.apis.alterra
import pytz
import requests

class Sugarbush(liftstatus.apis.alterra.AlterraMountain):
    """Implementation of :class:`liftstatus.Mountain` for Sugarbush, VT"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Sugarbush",
            server_url="https://v4.mtnfeed.com/resorts/sugarbush.json",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['LiftIcon'] in ['quad_chair']:
            if "Express" in lift['Name']:
                return liftstatus.LiftType.CLD_4
            else:
                return liftstatus.LiftType.CLF_4
        if lift['LiftIcon'] in ['triple_chair']:
            return liftstatus.LiftType.CLF_3
        if lift['LiftIcon'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['LiftIcon'] in ['magic_carpet']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['LiftIcon']}")
