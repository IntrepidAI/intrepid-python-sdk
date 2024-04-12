# from intrepid.api_manager import ApiManager
# from intrepid.bucketing_manager import BucketingManager
from intrepid.cache_manager import CacheManager
# from intrepid.config import DecisionApi
from intrepid.constants import WARNING_DEFAULT_CONFIG, TAG_INITIALIZATION
# from intrepid.decision_mode import DecisionMode
from intrepid.log_manager import LogLevel
# from intrepid.tracking_manager import TrackingManager
from intrepid.status import Status

class ConfigManager:

    def __init__(self):
        self.flagship_config = None
        self.decision_manager = None
        self.tracking_manager = None
        self.cache_manager = None

        # TODO