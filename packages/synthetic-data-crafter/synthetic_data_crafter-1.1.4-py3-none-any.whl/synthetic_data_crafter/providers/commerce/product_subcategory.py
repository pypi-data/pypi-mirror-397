from synthetic_data_crafter.providers.base_provider import BaseProvider


class ProductSubcategoryProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['product'], **kwargs)

    def generate_non_blank(self, row_data=None):
        col = self.get_random_data_by_list(
            ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'])

        product_name = row_data.get('product_name') if row_data else None

        if product_name:
            return self.get_dataset_lookup(
                'product', 'Product Name').get(product_name).get(col)

        return self.get_row_data_from_datasets('product', col)
