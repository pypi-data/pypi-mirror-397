
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class BigSky(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Big Sky, MT"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Big Sky",
            server_url="https://www.bigskyresort.com/api/reportpal?resortName=bs&useReportPal=true",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )
