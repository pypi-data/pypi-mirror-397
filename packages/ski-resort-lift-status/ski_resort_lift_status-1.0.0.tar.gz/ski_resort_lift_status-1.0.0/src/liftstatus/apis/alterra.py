
from abc import abstractmethod
import dateutil
import datetime
import liftstatus
import logging
import pprint
import requests

logger = logging.getLogger(__name__)

class AlterraMountain(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for Alterra-owned mountains
    
    :param server_url: Address of v4.mtnfeed.com JSON endpoint.
    :param timezone: Timezone where mountain is located
    :param session: Optional requests library session object
    :param resort_name: Selects which name in a multi-resort response that this mountain represents
    """

    def __init__(self, server_url: str, timezone: datetime.tzinfo, session: requests.Session, resort_name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._server_url = server_url
        self._timezone = timezone
        self._session = session
        self._resort_name = resort_name

    def get_lift_status(self, day_of_week: str = None):
        """Retrieves the status of each lift reported by the mountain's API

        :param day_of_week: Optional override of the current day of the week for determining hours
        :return: List of :class:`liftstatus.Lift` objects reported by the API
        :rtype: list[liftstatus.Lift]
        :raises liftstatus.exceptions.APIParseException: If an error occurs parsing the result JSON
        """

        (bearer_token, resort_ids) = self._find_bearer_token_and_resort_ids()

        logger.debug(f"Getting mountain status from mtnpowder feed")
        serverResponse = self._session.get(
            "https://mtnpowder.com/feed/v3.json",
            params={'bearer_token': bearer_token, 'resortId[]': resort_ids},
            headers={"User-Agent": liftstatus._USER_AGENT}
        )
        serverResponse.raise_for_status()

        jsonObject = serverResponse.json()
        logger.debug(pprint.pformat(jsonObject, indent=4))

        return_list = []
        if not "Resorts" in jsonObject or type(jsonObject['Resorts']) != list or len(jsonObject['Resorts']) == 0:
            raise liftstatus.exceptions.APIParseException("Missing Resort list in JSON response!")
        
        for resortJson in jsonObject['Resorts']:
            if self._resort_name is not None and resortJson['Name'] != self._resort_name:
                continue

            if not "MountainAreas" in resortJson or type(resortJson['MountainAreas']) != list or len(resortJson['MountainAreas']) == 0:
                raise liftstatus.exceptions.APIParseException("Missing Mountain Area dict in JSON response!")

            for mountainArea in resortJson['MountainAreas']:
                if not "Lifts" in mountainArea or type(mountainArea['Lifts']) != list:
                    raise liftstatus.exceptions.APIParseException("Missing Lifts list in JSON response!")
                
                if len(mountainArea['Lifts']) == 0:
                    continue
                
                for lift in mountainArea['Lifts']:

                    current_day_of_week = day_of_week
                    if current_day_of_week is None:
                        current_day_of_week = datetime.datetime.now(self._timezone).strftime('%A')
                    lift_hours = lift['Hours'][current_day_of_week]

                    open_time = None
                    if lift_hours['Open'] != '' and lift_hours['Open'] != 'Closed':
                        open_time = datetime.datetime.strptime(lift_hours['Open'], "%I:%M %p")
                        open_time = datetime.time(hour=open_time.hour, minute=open_time.minute, tzinfo=self._timezone)

                    closed_time = None
                    if lift_hours['Close'] != '' and lift_hours['Close'] != 'Closed':
                        closed_time = datetime.datetime.strptime(lift_hours['Close'], "%I:%M %p")
                        closed_time = datetime.time(hour=closed_time.hour, minute=closed_time.minute, tzinfo=self._timezone)

                    wait_time = None
                    # print(lift['WaitTime'], lift['WaitTimeString'], lift['WaitTimeStatus'])
                    # if 'WaitTimeInMinutes' in lift and lift['WaitTimeInMinutes'] is not None:
                    #     wait_time = datetime.timedelta(minutes=lift['WaitTimeInMinutes'])

                    return_list.append(liftstatus.Lift(
                        name=self._map_lift_name(lift),
                        type=self._map_lift_type(lift),
                        status=self._map_lift_status(lift),
                        updated_at=dateutil.parser.parse(lift['UpdateDate']),
                        open_time=open_time,
                        closed_time=closed_time,
                        wait_time=wait_time,
                    ))

        return return_list

    def _find_bearer_token_and_resort_ids(self):
        logger.debug(f"Requesting Bearer Token from Mountain Feed: {self._server_url} (User Agent: \"{liftstatus._USER_AGENT}\")")
        serverResponse = self._session.get(self._server_url, headers={"User-Agent": liftstatus._USER_AGENT})
        serverResponse.raise_for_status()

        jsonObject = serverResponse.json()
        if not "bearerToken" in jsonObject:
            raise liftstatus.exceptions.APIParseException("Missing Bearer Token in JSON response!")
        if not "resortIds" in jsonObject or type(jsonObject['resortIds']) != list or len(jsonObject['resortIds']) == 0:
            raise liftstatus.exceptions.APIParseException("Missing Resort ID in JSON response!")
        
        logger.debug(f"Bearer Token from mtnfeed: {jsonObject['bearerToken']}")
        return (jsonObject['bearerToken'], jsonObject['resortIds'])

    @abstractmethod
    def _map_lift_type(self, lift):
        pass

    def _map_lift_name(self, lift):
        return lift['Name']

    def _map_lift_status(self, lift):
        if lift['StatusEnglish'] in ['closed', 'closed_for_season', 'mechanical_closure', 'closed_opens_tomorrow']:
            return liftstatus.LiftStatus.CLOSED
        if lift['StatusEnglish'] == 'open':
            return liftstatus.LiftStatus.OPEN
        if lift['StatusEnglish'] == 'delayed':
            return liftstatus.LiftStatus.DELAYED
        if lift['StatusEnglish'] in ['hold', 'wind_hold', 'wind_closure']:
            return liftstatus.LiftStatus.HOLD
        if lift['StatusEnglish'] == 'open_ski_ride_school_only':
            return liftstatus.LiftStatus.RESTRICTED
        if lift['StatusEnglish'] in ['expected', 'scheduled']:
            return liftstatus.LiftStatus.SCHEDULED
            
        raise liftstatus.exceptions.APIParseException(f"Unknown Status value ({lift['StatusEnglish']}) for lift {lift['Name']}")
