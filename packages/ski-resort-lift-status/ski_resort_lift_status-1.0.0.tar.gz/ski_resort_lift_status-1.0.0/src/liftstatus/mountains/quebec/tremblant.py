
import liftstatus
import liftstatus.apis.alterra
import pytz
import requests

class Tremblant(liftstatus.apis.alterra.AlterraMountain):
    """Implementation of :class:`liftstatus.Mountain` for Mont Tremblant, QC"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Mont Tremblant",
            server_url="https://v4.mtnfeed.com/resorts/tremblant-en.json",
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
        if lift['LiftIcon'] in ['magic_carpet']:
            return liftstatus.LiftType.SL
        if lift['LiftIcon'] in ['gondola']:
            return liftstatus.LiftType.MGD
        if lift['LiftIcon'] in ['cabriolet']:
            return liftstatus.LiftType.CABRIO
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['LiftIcon']}")
