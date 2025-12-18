
import dateutil
import liftstatus
import logging
import pprint
import requests

logger = logging.getLogger(__name__)

class JacksonHole(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for Jackson Hole, WY"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(name="Jackson Hole")
        self._session = session

    def get_lift_status(self):
        server_url = "https://jacksonhole-prod.zaneray.com/api/all.json"
        logger.debug(f"Requesting Lift Status: {server_url} (User Agent: \"{liftstatus._USER_AGENT}\")")
        serverResponse = self._session.get(server_url, headers={"User-Agent": liftstatus._USER_AGENT})
        serverResponse.raise_for_status()
        responseJson = serverResponse.json()

        if responseJson is None or type(responseJson) != dict:
            raise liftstatus.exceptions.APIParseException("Failed to find JSON data from reportpal")

        if 'lifts' not in responseJson:
            raise liftstatus.exceptions.APIParseException("Failed to find lifts data from reportpal")

        return_list = []

        for lift in responseJson['lifts'].values():
            logger.debug(pprint.pformat(lift, indent=4))

            if lift['openingStatus'] == 'CLOSED':
                lift_status = liftstatus.LiftStatus.CLOSED
            elif lift['openingStatus'] == 'OPEN':
                lift_status = liftstatus.LiftStatus.OPEN
            else:
                raise liftstatus.exceptions.APIParseException(f"Unknown Status value for lift: {lift}")
            
            lift_type = liftstatus.LiftType.UNKNOWN
            if lift['liftType'] in ['DETACHABLE_CHAIRLIFT'] or lift['name'] in ['Thunder Quad']:
                if lift['name'].endswith(' Quad'):
                    lift_type = liftstatus.LiftType.CLD_4
                else:
                    raise liftstatus.exceptions.APIParseException(f"Unknown capacity for lift {lift['name']}")
            elif lift['liftType'] in ['CHAIRLIFT']:
                if lift['name'].endswith(' Quad'):
                    lift_type = liftstatus.LiftType.CLF_4
                elif lift['name'].endswith(' Double'):
                    lift_type = liftstatus.LiftType.CLF_2
                else:
                    raise liftstatus.exceptions.APIParseException(f"Unknown capacity for lift {lift['name']}")
            elif lift['liftType'] in ['GONDOLA']:
                lift_type = liftstatus.LiftType.MGD
            elif lift['liftType'] in ['TRAM']:
                lift_type = liftstatus.LiftType.ATW
            else:
                raise liftstatus.exceptions.APIParseException(f"Unknown Type value for lift {lift['name']}: {lift['liftType']}")
        
            
            # print(lift['openTime'])
            # lift_hours = lift['hours'].split(',')[0].split(' ')[0].replace('–', '-')
            # if len(lift_hours.split('-')) == 2:
            #     (open_time, closed_time) = lift_hours.split('-', maxsplit=1)
            #     def fix_time(val, is_pm):
            #         val = val.replace('M', '').replace('m', '')
            #         val = [int(x) for x in val[:-1].split(':')]
            #         if len(val) > 1:
            #             val = ((val[0] + 12) if is_pm else val[0]) * 100 + val[1]
            #         else:
            #             val = ((val[0] + 12) if is_pm else val[0]) * 100
            #         return val
                
            #     open_time = fix_time(open_time, False)
            #     closed_time = fix_time(closed_time, True)
            # else:
            #     open_time = None
            #     closed_time = None

            return_list.append(liftstatus.Lift(
                name=lift['name'],
                type=lift_type,
                status=lift_status,
                updated_at=dateutil.parser.parse(responseJson['lastModified']),
                open_time=0, # TODO: openTime
                closed_time=0, # TODO: closeTime
                wait_time=0 # TODO: lift['wait_time']
            ))

        return return_list
