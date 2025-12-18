
import liftstatus
import liftstatus.apis.aspen
import pytz
import requests

class Buttermilk(liftstatus.apis.aspen.AspenMountain):
    """Implementation of :class:`liftstatus.Mountain` for Buttermilk, CO"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Buttermilk",
            server_url="https://www.aspensnowmass.com/AspenSnowmass/LiftStatus/Feed?mountain=Buttermilk&areas=&isSummer=False",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )
