
import liftstatus
import liftstatus.apis.boyne
import pytz
import requests

class CypressMountain(liftstatus.apis.boyne.BoyneMountain):
    """Implementation of :class:`liftstatus.Mountain` for Cypress Mountain, BC"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Cypress Mountain",
            server_url="https://www.cypressmountain.com/api/reportpal?resortName=cy&useReportPal=true",
            timezone=pytz.timezone('America/Vancouver'),
            session=session
        )
