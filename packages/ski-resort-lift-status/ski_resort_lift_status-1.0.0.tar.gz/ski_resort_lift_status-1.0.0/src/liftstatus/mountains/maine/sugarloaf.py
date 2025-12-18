
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class Sugarloaf(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Sugarloaf, ME"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Sugarloaf",
            server_url="https://www.sugarloaf.com/api/reportpal?resortName=sl&useReportPal=true",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
