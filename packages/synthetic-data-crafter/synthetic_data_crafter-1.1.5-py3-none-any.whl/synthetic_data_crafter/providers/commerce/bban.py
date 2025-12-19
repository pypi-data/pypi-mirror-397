import random
import string
from synthetic_data_crafter.providers.base_provider import BaseProvider


class BbanProvider(BaseProvider):
    COUNTRY_BBAN_LENGTH = {
        "US": 16,       # United States
        "DE": 18,       # Germany
        "FR": 23,       # France
        "GB": 22,       # United Kingdom
        "NL": 18,       # Netherlands
        "IT": 23,       # Italy
        "ES": 20,       # Spain
        "BE": 16,       # Belgium
        "CH": 12,       # Switzerland
        "AT": 20,       # Austria
        "DK": 14,       # Denmark
        "SE": 24,       # Sweden
        "NO": 11,       # Norway
        "FI": 14,       # Finland
        "PT": 21,       # Portugal
        "PL": 24,       # Poland
        "IE": 22,       # Ireland
        "CZ": 20,       # Czech Republic
        "HU": 24,       # Hungary
        "RO": 24,       # Romania
        "GR": 23,       # Greece
        "SK": 20,       # Slovakia
        "SI": 19,       # Slovenia
    }

    ALPHANUMERIC_COUNTRIES = ["GB", "NL", "IT", "IE"]

    def __init__(self, blank_percentage: float = 0.0, country: str = "US", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.country = country.upper()
        self.length = self.COUNTRY_BBAN_LENGTH.get(self.country, 16)

    def generate_non_blank(self, row_data=None):
        if self.country in self.ALPHANUMERIC_COUNTRIES:
            chars = string.ascii_uppercase + string.digits
        else:
            chars = string.digits

        return ''.join(random.choices(chars, k=self.length))
