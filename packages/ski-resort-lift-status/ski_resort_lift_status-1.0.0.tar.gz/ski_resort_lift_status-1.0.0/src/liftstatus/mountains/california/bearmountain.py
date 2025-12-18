
import liftstatus
import liftstatus.apis.alterra
import pytz
import requests

class BearMountain(liftstatus.apis.alterra.AlterraMountain):
    """Implementation of :class:`liftstatus.Mountain` for Bear Mountain, CA"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Bear Mountain",
            server_url="https://v4.mtnfeed.com/resorts/big-bear-mountain.json",
            timezone=pytz.timezone('US/Pacific'),
            session=session,
            resort_name="Bear Mountain"
        )

    def _map_lift_type(self, lift):
        if lift['LiftIcon'] in ['six_chair', 'high_speed_six_chair']:
            return liftstatus.LiftType.CLD_6
        if lift['LiftIcon'] in ['high_speed_quad']:
            return liftstatus.LiftType.CLD_4
        if lift['LiftIcon'] in ['triple_chair']:
            return liftstatus.LiftType.CLF_3
        if lift['LiftIcon'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['LiftIcon'] in ['magic_carpet']:
            return liftstatus.LiftType.SL
        
        liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['LiftIcon']}")
