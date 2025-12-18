
from abc import abstractmethod
import dateutil
import datetime
import liftstatus
import logging
import pprint
import requests

logger = logging.getLogger(__name__)

class BoyneMountain(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for Boyne Resorts mountains
    
    :param server_url: Address of ReportPal JSON endpoint.
    :param timezone: Timezone where mountain is located
    :param session: Optional requests library session object
    """

    def __init__(self, server_url: str, timezone: datetime.tzinfo, session: requests.Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._server_url = server_url
        self._timezone = timezone
        self._session = session

    def get_lift_status(self):
        """Retrieves the status of each lift reported by the mountain's API

        :return: List of :class:`liftstatus.Lift` objects reported by the API
        :rtype: list[liftstatus.Lift]
        :raises liftstatus.exceptions.APIParseException: If an error occurs parsing the result JSON
        """

        logger.debug(f"Requesting Lift Status: {self._server_url} (User Agent: \"{liftstatus._USER_AGENT}\")")
        serverResponse = self._session.get(self._server_url, headers={"User-Agent": liftstatus._USER_AGENT})
        serverResponse.raise_for_status()
        responseJson = serverResponse.json()

        if responseJson is None or type(responseJson) != dict:
            raise liftstatus.exceptions.APIParseException("Failed to find JSON data from reportpal")

        if 'facilities' not in responseJson or 'areas' not in responseJson['facilities'] or 'area' not in responseJson['facilities']['areas']:
            raise liftstatus.exceptions.APIParseException("Failed to find area data from reportpal")

        return_list = []

        for area in responseJson['facilities']['areas']['area']:
            lifts = area.get('lifts', {}).get('lift', [])
            if lifts is None:
                continue
            for lift in lifts:
                logger.debug(pprint.pformat(lift, indent=4))

                open_time = None
                if lift['openTime'] is not None:
                    open_time = datetime.datetime.strptime(lift['openTime'], "%H:%M")
                    open_time = datetime.time(hour=open_time.hour, minute=open_time.minute, tzinfo=self._timezone)

                closed_time = None
                if lift['closeTime'] is not None:
                    closed_time = datetime.datetime.strptime(lift['closeTime'], "%H:%M")
                    closed_time = datetime.time(hour=closed_time.hour, minute=closed_time.minute, tzinfo=self._timezone)

                wait_time = None
                # print(lift['skierWaitTime'], lift['scenicWaitTime'])
                # if 'WaitTimeInMinutes' in lift and lift['WaitTimeInMinutes'] is not None:
                #     wait_time = datetime.timedelta(minutes=lift['WaitTimeInMinutes'])


                return_list.append(liftstatus.Lift(
                    name=self._map_lift_name(lift),
                    type=self._map_lift_type(lift),
                    status=self._map_lift_status(lift),
                    updated_at=dateutil.parser.parse(responseJson['liftsUpdated']),
                    open_time=open_time,
                    closed_time=closed_time,
                    wait_time=wait_time,
                ))

        return return_list

    def _map_lift_type(self, lift):
        if lift['type'] in ['Detachable Chairlift']:
            if lift['capacity'] == 8:
                return liftstatus.LiftType.CLD_8
            elif lift['capacity'] == 6:
                return liftstatus.LiftType.CLD_6
            elif lift['capacity'] == 4:
                return liftstatus.LiftType.CLD_4
            elif lift['capacity'] == 3:
                return liftstatus.LiftType.CLD_3
            else:
                raise liftstatus.exceptions.APIParseException(f"Unknown capacity value for lift {lift['name']}: {lift['capacity']}")
        elif lift['type'] in ['Chairlift']:
            if lift['capacity'] == 4:
                return liftstatus.LiftType.CLF_4
            elif lift['capacity'] == 3:
                return liftstatus.LiftType.CLF_3
            elif lift['capacity'] == 2:
                return liftstatus.LiftType.CLF_2
            else:
                raise liftstatus.exceptions.APIParseException(f"Unknown capacity value for lift {lift['name']}: {lift['capacity']}")
        elif lift['type'] in ['Gondola']:
            return liftstatus.LiftType.MGD
        elif lift['type'] in ['Chondola']:
            return liftstatus.LiftType.CGD
        elif lift['type'] in ['Aerial Tramway']:
            return liftstatus.LiftType.ATW
        elif lift['type'] in ['Magic Carpet', 'Magic carpet', 'Poma', 'Rope tow', 'T-Bar']:
            return liftstatus.LiftType.SL
        else:
            raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['name']}: {lift['type']}")
            
    def _map_lift_name(self, lift):
        return lift['name']

    def _map_lift_status(self, lift):
        if lift['status'] == 'Closed':
            return liftstatus.LiftStatus.CLOSED
        if lift['status'] == 'Open':
            return liftstatus.LiftStatus.OPEN
        if lift['status'] == 'Scheduled':
            return liftstatus.LiftStatus.SCHEDULED
        if lift['status'] == 'On Hold':
            return liftstatus.LiftStatus.HOLD
        if lift['status'] == 'Event':
            return liftstatus.LiftStatus.RESTRICTED
            
        raise liftstatus.exceptions.APIParseException(f"Unknown Status value ({lift['status']}) for lift {lift['name']}")
