from synthetic_data_crafter.providers.base_provider import BaseProvider
from typing import Callable, Any
import inspect


class LambdaProvider(BaseProvider):
    def __init__(self, func: Callable[..., Any], blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.func = func
        self.num_params = len(inspect.signature(func).parameters)

    def generate_non_blank(self, row_data=None):
        if self.num_params == 0:
            return self.func()
        else:
            return self.func(row_data)
