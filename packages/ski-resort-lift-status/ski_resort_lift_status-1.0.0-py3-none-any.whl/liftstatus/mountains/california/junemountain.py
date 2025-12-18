
import liftstatus
import liftstatus.apis.alterra
import pytz
import requests

class JuneMountain(liftstatus.apis.alterra.AlterraMountain):
    """Implementation of :class:`liftstatus.Mountain` for June Mountain, CA"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="June Mountain",
            server_url="https://v4.mtnfeed.com/resorts/june-mountain.json",
            timezone=pytz.timezone('US/Pacific'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['LiftIcon'] in ['quad_chair']:
            return liftstatus.LiftType.CLD_4
        if lift['LiftIcon'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['LiftIcon'] in ['magic_carpet']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['LiftIcon']}")
