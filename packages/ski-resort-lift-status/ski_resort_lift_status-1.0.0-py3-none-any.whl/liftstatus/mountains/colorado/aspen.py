
import liftstatus
import liftstatus.apis.aspen
import pytz
import requests

class AspenMountain(liftstatus.apis.aspen.AspenMountain):
    """Implementation of :class:`liftstatus.Mountain` for Aspen Mountain, CO"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Aspen Mountain",
            server_url="https://www.aspensnowmass.com/AspenSnowmass/LiftStatus/Feed?mountain=AspenMountain&areas=&isSummer=False",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )
