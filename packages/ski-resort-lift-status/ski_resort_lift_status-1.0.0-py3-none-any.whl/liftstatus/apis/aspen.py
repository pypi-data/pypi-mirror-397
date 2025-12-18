import requests
import pprint
import logging
import datetime

import liftstatus

logger = logging.getLogger(__name__)

class AspenMountain(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for Aspen mountains
    
    :param server_url: Address of LiftStatus JSON endpoint.
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

        if not "liftStatuses" in terrain_status or type(terrain_status['liftStatuses']) != list or len(terrain_status['liftStatuses']) == 0:
            return [] # Expected if resort is closed

        return_list = []
        for lift in terrain_status['liftStatuses']:
            lift_status = liftstatus.LiftStatus.UNKNOWN
            if lift['status'] == 'Closed':
                lift_status = liftstatus.LiftStatus.CLOSED
            elif lift['status'] == 'Open':
                lift_status = liftstatus.LiftStatus.OPEN
            elif lift['status'] == 'Delayed':
                lift_status = liftstatus.LiftStatus.DELAYED
            elif lift['status'] == 'Hold':
                lift_status = liftstatus.LiftStatus.HOLD
            else:
                raise liftstatus.exceptions.APIParseException(f"Unknown Status value for lift: {lift}")

            lift_type = liftstatus.LiftType.UNKNOWN
            if lift['type'] == 'Quad HS':
                lift_type = liftstatus.LiftType.CLD_4
            elif lift['type'] == 'Six HS':
                lift_type = liftstatus.LiftType.CLD_6
            elif lift['type'] == 'Triple HS':
                lift_type = liftstatus.LiftType.CLD_3
            elif lift['type'] == 'Double Fixed':
                lift_type = liftstatus.LiftType.CLF_2
            elif lift['type'] == 'Triple Fixed':
                lift_type = liftstatus.LiftType.CLF_3
            elif lift['type'] == 'Quad Fixed':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift['type'] in ['Gondola 8', 'Gondola 6']:
                lift_type = liftstatus.LiftType.MGD
            elif lift['type'] == 'Surface':
                lift_type = liftstatus.LiftType.SL
            else:
                raise ValueError((lift['liftName'], lift['type']))

            hours_of_operation = lift['hoursOfOperation'].split(' - ', maxsplit=2)
            
            open_time = None
            if hours_of_operation[0] != '0:00':
                open_time = datetime.datetime.strptime(hours_of_operation[0], "%I:%M %p")
                open_time = datetime.time(hour=open_time.hour, minute=open_time.minute, tzinfo=self._timezone)

            closed_time = None
            if hours_of_operation[1] != '0:00':
                closed_time = datetime.datetime.strptime(hours_of_operation[1], "%I:%M %p")
                closed_time = datetime.time(hour=closed_time.hour, minute=closed_time.minute, tzinfo=self._timezone)

            return_list.append(liftstatus.Lift(
                name=lift['liftName'],
                type=lift_type,
                status=lift_status,
                open_time=open_time,
                closed_time=closed_time,
                wait_time=datetime.timedelta(minutes=int(lift['time']))
            ))

        return return_list
