import requests
import logging
import datetime
from bs4 import BeautifulSoup
import liftstatus

logger = logging.getLogger(__name__)

class Loveland(liftstatus.Mountain):
    """Implementation of :class:`liftstatus.Mountain` for Loveland, CO"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(name="Loveland Basin/Valley")
        self._session = session

    def get_lift_status(self):
        status_url = "https://skiloveland.com/trail-lift-report/"
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        logger.debug(f"Requesting Lift Status: {status_url} (User Agent: \"{liftstatus._USER_AGENT}\")")
        serverResponse = self._session.get(status_url, headers={"User-Agent": liftstatus._USER_AGENT})
        serverResponse.raise_for_status()

        soup = BeautifulSoup(serverResponse.text, 'html.parser')
        lift_opts = soup.select('h2.tablepress-table-name')
        
        return_list = []
        for lift_opt in lift_opts:
            lift_opt = lift_opt.text.strip().replace(' -', '-').replace('- ', '-')

            lift_name = lift_opt.split('-')[0].replace('PTARMIGAN LIFT', 'Ptarmigan')
            lift_status = liftstatus.LiftStatus[lift_opt.split('-')[1]]

            lift_type = liftstatus.LiftType.UNKNOWN
            if lift_name == 'Rainbow Magic Carpet':
                lift_type = liftstatus.LiftType.SL
            elif lift_name == 'Chet\'s Dream':
                lift_type = liftstatus.LiftType.CLD_4
            elif lift_name == 'Lift 2':
                lift_type = liftstatus.LiftType.CLF_3
            elif lift_name == 'Lift 3':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift_name == 'Lift 4':
                lift_type = liftstatus.LiftType.CLF_3
            elif lift_name == 'Lift 6':
                lift_type = liftstatus.LiftType.CLF_3
            elif lift_name == 'Lift 7':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift_name == 'Lift 8':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift_name == 'Lift 9':
                lift_type = liftstatus.LiftType.CLF_4
            elif lift_name == 'Ptarmigan':
                lift_type = liftstatus.LiftType.CLF_3
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
