
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class BoyneHighlands(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Boyne Highlands, MI"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Boyne Highlands",
            server_url="https://www.highlandsharborsprings.com/api/reportpal?resortName=th&useReportPal=true",
            timezone=pytz.timezone('US/Eastern'),
            session=session
        )
