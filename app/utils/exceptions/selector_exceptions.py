class SelectorErrorBase(Exception):
    def __init__(self, selector_name, selector):
        self.message = "Cannot select <{}> with selector: '{}'".format(selector_name, selector)
        super().__init__(self.message)


class ProductInfoSelectorError(SelectorErrorBase):
    name = 'Product Info'
    def __init__(self, selector):
        super().__init__(self.name, selector)


class TitleSelectorError(SelectorErrorBase):
    name = 'Title'
    def __init__(self, selector):
        super().__init__(self.name, selector)


class PriceSelectorError(SelectorErrorBase):
    name = 'Price'
    def __init__(self, selector):
        super().__init__(self.name, selector)


class KeyFeatureSelectorError(SelectorErrorBase):
    name = 'Key Feature'
    def __init__(self, selector):
        super().__init__(self.name, selector)


class SpecTableSelectorError(SelectorErrorBase):
    name = 'Spec Table'
    def __init__(self, selector):
        super().__init__(self.name, selector)


class ListItemSelectorError(SelectorErrorBase):
    name = 'List Item'
    def __init__(self, selector):
        super().__init__(self.name, selector)