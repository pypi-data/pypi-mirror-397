
from abc import abstractmethod
from bs4 import BeautifulSoup
import datetime
import dateutil
import json
import liftstatus
import logging
import pprint
import requests

logger = logging.getLogger(__name__)

class EpicMountain(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for Vail Resorts mountains
    
    :param server_url: Address of lift-and-terrain-status.aspx HTML page.
    :param timezone: Timezone where mountain is located
    :param session: Optional requests library session object"""

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
        
        terrain_status = self._find_terrain_status()
        logger.debug(pprint.pformat(terrain_status, indent=4))

        if not "Lifts" in terrain_status or type(terrain_status['Lifts']) != list or len(terrain_status['Lifts']) == 0:
            return [] # Expected if resort is closed
        
        return_list = []
        for lift in terrain_status['Lifts']:
            open_time = None
            if 'OpenTime' in lift and lift['OpenTime'] is not None:
                open_time = datetime.datetime.strptime(lift['OpenTime'], "%H:%M")
                open_time = datetime.time(hour=open_time.hour, minute=open_time.minute, tzinfo=self._timezone)
            
            closed_time = None
            if 'CloseTime' in lift and lift['CloseTime'] is not None:
                closed_time = datetime.datetime.strptime(lift['CloseTime'], "%H:%M")
                closed_time = datetime.time(hour=closed_time.hour, minute=closed_time.minute, tzinfo=self._timezone)

            wait_time = None
            if 'WaitTimeInMinutes' in lift and lift['WaitTimeInMinutes'] is not None:
                wait_time = datetime.timedelta(minutes=lift['WaitTimeInMinutes'])

            return_list.append(liftstatus.Lift(
                name=self._map_lift_name(lift),
                type=self._map_lift_type(lift),
                status=self._map_lift_status(lift),
                updated_at=dateutil.parser.parse(terrain_status['Date']),
                open_time=open_time,
                closed_time=closed_time,
                wait_time=wait_time,
            ))

        return return_list
    
    def _find_terrain_status(self):
        logger.debug(f"Requesting Lift Status: {self._server_url} (User Agent: \"{liftstatus._USER_AGENT}\")")
        serverResponse = self._session.get(self._server_url, headers={"User-Agent": liftstatus._USER_AGENT})
        serverResponse.raise_for_status()

        soup = BeautifulSoup(serverResponse.text, 'html.parser')
        script_modules = soup.find_all('script', type="module")

        terrain_status_feeds = []
        for module in script_modules:
            terrain_status_feed = None
            for line in module.text.split("\n"):
                if 'FR.TerrainStatusFeed' in line:
                    terrain_status_feed = line.split(' = ', maxsplit=2)[1].strip()
                    terrain_status_feed = terrain_status_feed[:-1]
                    terrain_status_feeds.append(terrain_status_feed)

        terrain_status = None
        for terrain_status_feed in terrain_status_feeds:
            terrain_status = json.loads(terrain_status_feed)

            # Hack: As of 2025 season, Vail added two different terrain status feeds,
            # that are nearly identical but one of them uses strings for status
            # and one uses ints. We want the one with strings, so we skip the one with
            # ints (identified by the date being a JS date and not an ISO date)
            if "Date(" not in terrain_status["Date"]:
                return terrain_status

        raise liftstatus.exceptions.APIParseException("Failed to find JSON data from FR.TerrainStatusFeed")

    @abstractmethod
    def _map_lift_type(self, lift):
        pass

    def _map_lift_name(self, lift):
        return lift['Name']

    def _map_lift_status(self, lift):
        if lift['Status'] == 'Closed':
            return liftstatus.LiftStatus.CLOSED
        if lift['Status'] == 'Open':
            return liftstatus.LiftStatus.OPEN
        if lift['Status'] == 'Scheduled':
            return liftstatus.LiftStatus.SCHEDULED
        if lift['Status'] in ['OnHold']:
            return liftstatus.LiftStatus.HOLD
            
        raise liftstatus.exceptions.APIParseException(f"Unknown Status value ({lift['Status']}) for lift {lift['Name']}")
