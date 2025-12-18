
import liftstatus
import liftstatus.apis.alterra
import pytz
import requests

class SnowValley(liftstatus.apis.alterra.AlterraMountain):
    """Implementation of :class:`liftstatus.Mountain` for Snow Valley, CA"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Snow Valley",
            server_url="https://v4.mtnfeed.com/resorts/big-bear-mountain.json",
            timezone=pytz.timezone('US/Pacific'),
            session=session,
            resort_name="Snow Valley"
        )

    def _map_lift_type(self, lift):
        if lift['LiftIcon'] in ['six_chair']:
            return liftstatus.LiftType.CLD_6
        if lift['LiftIcon'] in ['triple_chair']:
            return liftstatus.LiftType.CLF_3
        if lift['LiftIcon'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['LiftIcon'] in ['magic_carpet']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['LiftIcon']}")
