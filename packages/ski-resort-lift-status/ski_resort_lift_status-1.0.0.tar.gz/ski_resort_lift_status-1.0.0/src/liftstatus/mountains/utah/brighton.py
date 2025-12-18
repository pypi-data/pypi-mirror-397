
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class Brighton(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Brighton, UT"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Brighton",
            server_url="https://www.brightonresort.com/api/reportpal?resortName=br&useReportPal=true",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )
