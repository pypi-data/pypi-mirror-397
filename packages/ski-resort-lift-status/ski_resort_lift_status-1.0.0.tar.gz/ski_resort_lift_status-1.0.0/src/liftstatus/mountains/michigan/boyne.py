
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class BoyneMountain(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Boyne Mountain, MI"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Boyne Mountain",
            server_url="https://www.boynemountain.com/api/reportpal?resortName=bm&useReportPal=true",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
