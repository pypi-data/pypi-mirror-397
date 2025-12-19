import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from .fetch_data import fetch_data

from pandas.core.base import PandasObject

# add the fetch_data method to the pandas DataFrame
PandasObject.fetch_data = fetch_data

class DeltaAgent:

    from .get_azure_service_client import get_azure_service_client
    from .validate_attrs import validate_attrs
    from .parse_log_as_df import parse_log_as_df

    def __init__(self, account_name=None, account_key=None, container_name=None, table_path=None):

        self.account_name = account_name
        self.account_key = account_key
        self.container_name = container_name
        self.table_path = table_path
    
    
    