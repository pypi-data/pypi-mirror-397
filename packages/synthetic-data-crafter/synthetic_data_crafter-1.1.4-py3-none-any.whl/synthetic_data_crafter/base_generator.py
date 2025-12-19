from .provider_factory import ProviderFactory
from typing import List, Dict, Any
import random


class BaseGenerator:

    def __init__(self, schema: List[Dict[str, Any]]):
        """
        Schema: Format in array of dicts describing each column.

        Example:
        [
            {
                "label": "First Name",
                "group": "personal",
                "key_label": "first_name",
                "options": {"blank_percentage": 0.1}
            },
            {
                "label": "Character Sequence",
                "group": "advanced",
                "key_label": "character_sequence",
                "options": {"format": "@@##", "blank_percentage": 0.05}
            }
        ]
        """

        self.schema = schema
        self.providers = self._initialize_providers()

    def generate_many(self, n: int):
        internal_rows = [{} for _ in range(n)]
        row_data_list = [{} for _ in range(n)]

        for _, data in self.providers.items():
            label = data["label"]
            provider = data["provider"]
            key_label = data["key_label"]

            # Compute blanks
            pct = getattr(provider, "blank_percentage", 0.0) or 0.0
            num_blanks = round(n * pct)
            blank_indices = set(random.sample(
                range(n), num_blanks)) if num_blanks > 0 else set()

            for i in range(n):
                if i in blank_indices:
                    internal_rows[i][label] = None
                    row_data_list[i][key_label] = None
                    continue

                if provider.__class__.__name__ == "TemplateProvider" or provider.__class__.__name__ == "LambdaProvider":
                    value = provider.generate_non_blank(
                        row_data=internal_rows[i])
                else:
                    value = provider.generate_non_blank(
                        row_data=row_data_list[i])

                internal_rows[i][label] = value
                row_data_list[i][key_label] = value

        return internal_rows

    def _initialize_providers(self):
        providers = {}
        schema_labels = [col["label"] for col in self.schema]

        for col in self.schema:
            label = col["label"]
            group = col["group"]
            key_label = col["key_label"]
            options = col.get("options", {})
            options["schema_labels"] = schema_labels

            provider_instance = ProviderFactory.create(
                group=group, label=key_label, **options)

            providers[label] = {
                "provider": provider_instance,
                "label": label,
                "key_label": key_label
            }

        return providers
