
import liftstatus
import liftstatus.apis.aspen
import pytz
import requests

class AspenHighlands(liftstatus.apis.aspen.AspenMountain):
    """Implementation of :class:`liftstatus.Mountain` for Aspen Highlands, CO"""

    def __init__(self, session: requests.Session = requests.Session()):
        super().__init__(
            name="Aspen Highlands",
            server_url="https://www.aspensnowmass.com/AspenSnowmass/LiftStatus/Feed?mountain=AspenHighlands&areas=&isSummer=False",
            timezone=pytz.timezone('US/Mountain'),
            session=session
        )
