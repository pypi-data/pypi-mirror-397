from bs4 import BeautifulSoup
import liftstatus
import logging
import requests

logger = logging.getLogger(__name__)

class ArapahoeBasin(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for Arapahoe Basin, CO"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(name="Arapahoe Basin")
        self._session = session

    def get_lift_status(self):
        status_url = "https://www.arapahoebasin.com/snow-report/"
        logger.debug(f"Requesting Lift Status: {status_url} (User Agent: \"{liftstatus._USER_AGENT}\")")
        serverResponse = self._session.get(status_url, headers={"User-Agent": liftstatus._USER_AGENT})
        serverResponse.raise_for_status()

        soup = BeautifulSoup(serverResponse.text, 'html.parser')
        lift_opts = soup.select('li.lift-opt')
        
        return_list = []
        lift_names = []
        for lift_opt in lift_opts:
            lift_opt = lift_opt.select_one('span')
            if "(Lift)" not in lift_opt.text:
                continue

            lift_name = lift_opt.text.strip().replace("  (Lift)", "")
            if lift_name in lift_names:
                continue
            lift_names.append(lift_name)
            lift_status_str = lift_opt.select_one('img[src]')
            lift_status_str = lift_status_str['src'].replace('.svg', '').split('/')[-1]

            lift_status = liftstatus.LiftStatus.UNKNOWN
            if lift_status_str == 'closed':
                lift_status = liftstatus.LiftStatus.CLOSED
            elif lift_status_str == 'open':
                lift_status = liftstatus.LiftStatus.OPEN
            else:
                raise ValueError((lift_name, lift_status_str))

            lift_type = liftstatus.LiftType.UNKNOWN
            if lift_name == 'Black Mountain Express Lift':
                lift_type = liftstatus.LiftType.CLD_4
            elif lift_name == 'Lenawee Express Lift': # 2 entries?
                lift_type = liftstatus.LiftType.CLD_6
            elif lift_name == 'Pallavicini Lift': # 2 entries?
                lift_type = liftstatus.LiftType.CLF_2
            elif lift_name == 'Beavers':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift_name == 'Zuma Lift':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift_name == 'Lazy J Tow':
                lift_type = liftstatus.LiftType.SL
            elif lift_name == 'Molly Hogan Lift':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift_name == 'Molly\'s Magic Carpet':
                lift_type = liftstatus.LiftType.SL
            elif lift_name == 'Pika Place Carpet':
                lift_type = liftstatus.LiftType.SL
            else:
                raise ValueError(lift_name)
            
            return_list.append(liftstatus.Lift(
                name=lift_name,
                type=lift_type,
                status=lift_status,
                updated_at=None,
                open_time=None,
                closed_time=None,
                wait_time=None,
            ))

        return return_list
