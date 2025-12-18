
import liftstatus
import liftstatus.apis.aspen
import pytz
import requests

class Snowmass(liftstatus.apis.aspen.AspenMountain):
    """Implementation of :class:`liftstatus.Mountain` for Snowmass, CO"""
    
    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Snowmass",
            server_url="https://www.aspensnowmass.com/AspenSnowmass/LiftStatus/Feed?mountain=Snowmass&areas=&isSummer=False",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )
