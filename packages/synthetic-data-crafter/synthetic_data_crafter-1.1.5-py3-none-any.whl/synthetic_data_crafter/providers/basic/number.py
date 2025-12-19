from synthetic_data_crafter.providers.base_provider import BaseProvider


class NumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, min: float = 0, max: float = 1000, decimals: int = 0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.min = min
        self.max = max
        self.decimals = decimals

    def generate_non_blank(self, row_data=None):
        amount = self.generate_number(self.min, self.max)
        value = round(amount, self.decimals)
        return int(value) if self.decimals == 0 else float(value)
