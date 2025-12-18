
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class SundayRiver(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Sunday River, ME"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Sunday River",
            server_url="https://www.sundayriver.com/api/reportpal?resortName=sr&useReportPal=true",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
