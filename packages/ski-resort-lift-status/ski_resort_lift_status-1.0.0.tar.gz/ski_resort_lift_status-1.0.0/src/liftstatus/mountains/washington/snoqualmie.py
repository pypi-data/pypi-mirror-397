
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class Snoqualmie(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Snoqualmie, WA"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Summit at Snoqualmie",
            server_url="https://www.summitatsnoqualmie.com/api/reportpal?resortName=ss&useReportPal=true",
            timezone=pytz.timezone('US/Pacific'),
            session=session
        )
