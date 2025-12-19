from azure.storage.filedatalake import DataLakeServiceClient

def get_azure_service_client(self, account_name=None, account_key=None):

        # the account_name and account_key will also be reconfigured by this method if they are provided as args
        if account_name is not None:
            self.account_name = account_name
        if account_key is not None:
            self.account_key = account_key

        req_attrs_ls = ['account_name', 'account_key']

        if self.validate_attrs(req_attrs_ls):

            azure_service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", self.account_name), credential=self.account_key)

            return azure_service_client