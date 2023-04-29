from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import ssl


class TLSAdapter(HTTPAdapter):
    """Transport adapter that forces use of TLSv1.2.
            All Tomcat Servers Require TLSv1.2 in DEV, QA, CTE or PROD environment."""

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        """Create and initialize the urllib3 PoolManager to use TLSv.12."""
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=ssl.PROTOCOL_TLSv1_2)
