
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class PleasantMountain(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Pleasant Mountain, ME"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Pleasant Mountain",
            server_url="https://www.pleasantmountain.com/api/reportpal?resortName=pm&useReportPal=true",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
