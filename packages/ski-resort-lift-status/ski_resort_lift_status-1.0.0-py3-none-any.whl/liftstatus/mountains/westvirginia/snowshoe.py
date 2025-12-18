
import liftstatus
import liftstatus.apis.alterra
import pytz
import requests

class Snowshoe(liftstatus.apis.alterra.AlterraMountain):
    """Implementation of :class:`liftstatus.Mountain` for Snowshoe, WV"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Snowshoe",
            server_url="https://v4.mtnfeed.com/resorts/snowshoe.json",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['LiftIcon'] in ['high_speed_quad']:
            return liftstatus.LiftType.CLD_4
        if lift['LiftIcon'] in ['quad_chair']:
            return liftstatus.LiftType.CLF_4
        if lift['LiftIcon'] in ['triple_chair']:
            return liftstatus.LiftType.CLF_3
        if lift['LiftIcon'] in ['magic_carpet', 'rope_tow']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['LiftIcon']}")
