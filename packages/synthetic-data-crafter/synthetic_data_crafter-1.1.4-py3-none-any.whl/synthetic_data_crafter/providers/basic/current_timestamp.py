from synthetic_data_crafter.providers.base_provider import BaseProvider
from datetime import datetime


class CurrentTimestampProvider(BaseProvider):
    DEFAULT_FORMATS = [
        "%Y-%m-%d",                      # 2025-11-21
        "%Y-%m-%d %H:%M:%S",             # 2025-11-21 14:55:00
        "%Y-%m-%d %H:%M:%S.%f",          # 2025-11-21 14:55:00.123456
        "%Y-%m-%dT%H:%M:%S.%fZ",         # 2025-11-21T14:55:00.123Z
        "%Y-%m-%dT%H:%M:%SZ",            # 2025-11-21T14:55:00Z
        "%Y/%m/%d",                      # 2025/11/21
        "%Y/%m/%d %H:%M:%S",             # 2025/11/21 14:55:00
        "%Y-%m-%dT%H:%M:%S",             # 2025-11-21T14:55:00 (ISO)
        "%d-%m-%Y",                      # 21-11-2025
        "%m-%d-%Y",                      # 11-21-2025
        "%b %d, %Y",                     # Nov 21, 2025
        "%B %d, %Y",                     # November 21, 2025
    ]

    def __init__(self, blank_percentage: float = 0.0, format: str = "%Y-%m-%d %H:%M:%S", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.format = format

    def generate_non_blank(self, row_data=None):
        now = datetime.now()
        if isinstance(self.format, (list, tuple)):
            fmt = self.get_random_data_by_list(self.format)
        else:
            fmt = self.format or self.DEFAULT_FORMATS[0]

        return now.strftime(fmt)
