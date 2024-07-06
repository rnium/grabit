class BaseSiteError(Exception):
    pass

class UnSupportedSiteError(BaseSiteError):
    def __init__(self):
        self.message = 'Site is not configured in sites.yaml'
        super().__init__(self.message)

class NotAProductError(BaseSiteError):
    def __init__(self, sitename):
        self.message = 'Not a product of {}'.format(sitename)
        super().__init__(self.message)