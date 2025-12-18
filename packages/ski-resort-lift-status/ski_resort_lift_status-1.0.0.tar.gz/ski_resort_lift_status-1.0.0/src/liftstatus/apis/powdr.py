
from abc import abstractmethod
import datetime
import liftstatus
import logging
import pprint
import requests

logger = logging.getLogger(__name__)

class POWDRMountain(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for POWDR-owned mountains
    
    :param server_url: Address of /api/v1/dor/drupal/lifts JSON endpoint.
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

        terrain_status = serverResponse.json()
        logger.debug(pprint.pformat(terrain_status, indent=4))

        return_list = []

        if terrain_status is None or type(terrain_status) != list:
            raise liftstatus.exceptions.APIParseException("Failed to find lift list in JSON response")
        
        for lift in terrain_status:
            return_list.append(liftstatus.Lift(
                name=self._map_lift_name(lift),
                type=self._map_lift_type(lift),
                status=self._map_lift_status(lift),
                updated_at=datetime.datetime.fromtimestamp(lift['updated'], datetime.UTC),
                open_time=self._map_open_time(lift),
                closed_time=self._map_closed_time(lift),
                wait_time=datetime.timedelta(minutes=int(lift['wait_time'])) if lift['wait_time'] != '' else None
            ))

        return return_list

    @abstractmethod
    def _map_lift_type(self, lift):
        pass

    def _map_lift_name(self, lift):
        return lift['name']

    def _map_lift_status(self, lift):
        if lift['status'] == 'closed':
            return liftstatus.LiftStatus.CLOSED
        if lift['status'] == 'open':
            return liftstatus.LiftStatus.OPEN
        if lift['status'] == 'delayed':
            return liftstatus.LiftStatus.DELAYED
        if lift['status'] in ['hold', 'on_hold']:
            return liftstatus.LiftStatus.HOLD
        if lift['status'] == 'expected':
            return liftstatus.LiftStatus.SCHEDULED

        raise liftstatus.exceptions.APIParseException(f"Unknown Status value ({lift['status']}) for lift {lift['name']}")

    def _map_open_time(self, lift):
        return None

    def _map_closed_time(self, lift):
        return None