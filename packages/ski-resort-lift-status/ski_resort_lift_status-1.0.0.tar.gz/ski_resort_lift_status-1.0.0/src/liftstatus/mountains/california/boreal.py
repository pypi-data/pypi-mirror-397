
import liftstatus
import liftstatus.apis.powdr
import pytz
import requests
import datetime

class Boreal(liftstatus.apis.powdr.POWDRMountain):
    """Implementation of :class:`liftstatus.Mountain` for Boreal, CA"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Boreal",
            server_url="https://api.rideboreal.com/api/v1/dor/drupal/lifts",
            timezone=pytz.timezone('US/Pacific'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['type'] in ['quad']:
            if lift['name'] in ['Accelerator Express Quad Charilift']:
                return liftstatus.LiftType.CLD_4
            else:
                return liftstatus.LiftType.CLF_4
        if lift['type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['type'] in ['surface', 'carpet']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['name']}: {lift['type']}")
    
    def _map_open_time(self, lift):
        if lift['hours'].strip() == '':
            return None
        return self._map_time(lift['hours'].split(' - ')[0])

    def _map_closed_time(self, lift):
        if lift['hours'].strip() == '':
            return None
        return self._map_time(lift['hours'].split(' - ')[1])
    
    def _map_time(self, time_segment):
        if ':' in time_segment:
            time_segment = datetime.datetime.strptime(time_segment.upper(), "%I:%M%p")
        else:
            time_segment = datetime.datetime.strptime(time_segment.upper(), "%I%p")
        
        return datetime.time(hour=time_segment.hour, minute=time_segment.minute, tzinfo=self._timezone)