
import liftstatus
import liftstatus.apis.powdr
import pytz
import requests
import datetime

def _day_text_to_num_of_week(day):
    if day.upper() in ['M', 'MON', 'MONDAY']:
        return 1
    if day.upper() in ['T', 'TU', 'TUESDAY']:
        return 2
    if day.upper() in ['W', 'WED', 'WEDNESDAY']:
        return 3
    if day.upper() in ['TH', 'THU', 'THURSDAY']:
        return 4
    if day.upper() in ['F', 'FRI', 'FRIDAY']:
        return 5
    if day.upper() in ['S', 'SA', 'SAT', 'SATURDAY']:
        return 6
    if day.upper() in ['SU', 'SUN', 'SUNDAY']:
        return 0
    raise ValueError(f"Unrecognized date text: {day}")

class Eldora(liftstatus.apis.powdr.POWDRMountain):
    """Implementation of :class:`liftstatus.Mountain` for Eldora, CO"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Eldora",
            server_url="https://api.eldora.com/api/v1/dor/drupal/lifts",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )

    def _map_lift_type(self, lift):
        if lift['type'] in ['six_person']:
            return liftstatus.LiftType.CLD_6
        if lift['type'] in ['quad']:
            return liftstatus.LiftType.CLF_4
        if lift['type'] in ['triple']:
            return liftstatus.LiftType.CLF_3
        if lift['type'] in ['double']:
            return liftstatus.LiftType.CLF_2
        if lift['type'] in ['surface', 'carpet']:
            return liftstatus.LiftType.SL
        
        raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['name']}: {lift['type']}")

    def _map_lift_status(self, lift):
        if lift['hours'] in ['Race Training Only']:
            return liftstatus.LiftStatus.RESTRICTED
        return super()._map_lift_status(lift)

    def _map_open_time(self, lift):
        if lift['hours'] in ['Race Training Only']:
            return None
        time_segment = self._get_time_segment(lift)
        if time_segment is None:
            return None
        return self._map_time(time_segment.split(' to ')[0])

    def _map_closed_time(self, lift):
        if lift['hours'] in ['Race Training Only']:
            return None
        time_segment = self._get_time_segment(lift)
        if time_segment is None:
            return None
        return self._map_time(time_segment.split(' to ')[1])
    
    def _get_time_segment(self, lift):
        current_day_of_week = int(datetime.datetime.now(self._timezone).strftime('%w'))
        for hours_option in lift['hours'].split('|'):
            (hours, days) = hours_option.strip().split(', ', maxsplit=2)
            if '/' in days:
                # One of listed days
                for day in days.split('/'):
                    if current_day_of_week == _day_text_to_num_of_week(day):
                        return hours
            elif '-' in days:
                # Range of days
                first_day, second_day = days.split('-')
                first_day = _day_text_to_num_of_week(first_day)
                second_day = _day_text_to_num_of_week(second_day)
                if second_day < first_day:
                    second_day += 7

                for i in range(first_day, second_day + 1):
                    if current_day_of_week == (i % 7):
                        return hours
            else:
                # Only one day
                if current_day_of_week == _day_text_to_num_of_week(days):
                    return hours
        
        return None
    
    def _map_time(self, time_segment):
        time_segment = time_segment.upper() # am -> AM
        time_segment = time_segment.replace('M', '') # AM -> A
        time_segment += 'M' # A -> AM

        if ':' in time_segment:
            time_segment = datetime.datetime.strptime(time_segment, "%I:%M%p")
        else:
            time_segment = datetime.datetime.strptime(time_segment, "%I%p")

        return datetime.time(hour=time_segment.hour, minute=time_segment.minute, tzinfo=self._timezone)