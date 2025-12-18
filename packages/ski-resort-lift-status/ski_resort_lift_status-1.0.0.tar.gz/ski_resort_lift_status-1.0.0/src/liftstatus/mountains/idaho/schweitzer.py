
import liftstatus
import liftstatus.apis.alterra
import pytz
import requests

class Schweitzer(liftstatus.apis.alterra.AlterraMountain):
    """Implementation of :class:`liftstatus.Mountain` for Schweitzer, ID"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Schweitzer",
            server_url="https://v4.mtnfeed.com/resorts/schweitzer.json",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['LiftIcon'] in ['high_speed_quad']:
            return liftstatus.LiftType.CLD_4
        if lift['LiftIcon'] in ['six_chair']:
            return liftstatus.LiftType.CLD_6
        if lift['LiftIcon'] in ['triple_chair']:
            return liftstatus.LiftType.CLF_3
        if lift['LiftIcon'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['LiftIcon'] in ['magic_carpet', 't_bar']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['LiftIcon']}")
