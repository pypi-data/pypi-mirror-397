
from .get_pqt_info_from_log import get_pqt_info_from_log

def parse_log_as_df(self, container_name=None, table_path=None):

        # the account_name and account_key will also be reconfigured by this method if they are provided as args
        if container_name is not None:
            self.container_name = container_name
        if table_path is not None:
            self.table_path = table_path

        azure_service_client = self.get_azure_service_client()

        req_attrs_ls = ['container_name', 'table_path']

        if self.validate_attrs(req_attrs_ls):
            df_pqt_wt_ptn = get_pqt_info_from_log(azure_service_client, self.container_name, self.table_path)

            propagete_attrs_ls = ['account_name', 'account_key', 'container_name', 'table_path']

            for attr in propagete_attrs_ls:
                df_pqt_wt_ptn.attrs[attr] = getattr(self, attr)

            return df_pqt_wt_ptn