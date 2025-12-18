
import liftstatus
import liftstatus.apis.epic
import pytz
import requests

class CrotchedMountain(liftstatus.apis.epic.EpicMountain):
    """Implementation of :class:`liftstatus.Mountain` for Crotched Mountain, NH"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Crotched Mountain",
            server_url="https://www.crotchedmtn.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )

    def _map_lift_type(self, lift):
        # if lift['Type'] in ['eight']:
        #     return liftstatus.LiftType.CLD_8
        # if lift['Type'] in ['six']:
        #     return liftstatus.LiftType.CLD_6
        if lift['Type'] in ['quad']:
            if lift['Name'] in ['Rocket']:
                return liftstatus.LiftType.CLD_4
            else:
                return liftstatus.LiftType.CLF_4
        if lift['Type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['Type'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['Type'] in ['conveyor']:
            return liftstatus.LiftType.SL
        # if lift['Type'] in ['gondola']:
        #     if lift['Name'] == "PEAK 2 PEAK Gondola":
        #         return liftstatus.LiftType.TGD
        #     else:
        #         return liftstatus.LiftType.MGD
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['Name']}: {lift['Type']}")
