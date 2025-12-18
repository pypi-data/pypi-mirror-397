
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class LoonMountain(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Loon Mountain, UT"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Loon Mountain",
            server_url="https://www.loonmtn.com/api/reportpal?resortName=lm&useReportPal=true",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
