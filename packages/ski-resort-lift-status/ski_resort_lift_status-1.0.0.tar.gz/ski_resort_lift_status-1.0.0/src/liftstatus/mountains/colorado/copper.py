
import liftstatus
import liftstatus.apis.powdr
import pytz
import requests
import datetime

class Copper(liftstatus.apis.powdr.POWDRMountain):
    """Implementation of :class:`liftstatus.Mountain` for Copper, CO"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Copper Mountain",
            server_url="https://api.coppercolorado.com/api/v1/dor/drupal/lifts",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['type'] in ['six_person']:
            return liftstatus.LiftType.CLD_6
        if lift['type'] in ['quad']:
            return liftstatus.LiftType.CLD_4
        if lift['type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['type'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['type'] in ['surface', 'carpet']:
            return liftstatus.LiftType.SL
        if lift['type'] in ['telemix']:
            return liftstatus.LiftType.CGD
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['name']}: {lift['type']}")

    def _map_open_time(self, lift):
        return self._map_time(lift['hours'].split('-')[0])

    def _map_closed_time(self, lift):
        return self._map_time(lift['hours'].split('-')[1])
    
    def _map_time(self, time_segment):
        time_segment = time_segment.upper() # am -> AM
        time_segment = time_segment.replace('M', '') # AM -> A
        time_segment += 'M' # A -> AM

        if ':' in time_segment:
            time_segment = datetime.datetime.strptime(time_segment, "%I:%M%p")
        else:
            time_segment = datetime.datetime.strptime(time_segment, "%I%p")

        return datetime.time(hour=time_segment.hour, minute=time_segment.minute, tzinfo=self._timezone)