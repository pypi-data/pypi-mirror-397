# DeltaAgent - Deltalake Agent

This library can used to fetch data from deltalake tables without the dependency on Spark clusters. It is developed based on the `pandas`, `adlfs` and `Office365-REST-Python-Client` libraries.

## Use cases and benefits

To use the library, firstly we need to install the it by

```
pip install DeltaAgent
```

It requires the datalake `account_name` and `account_key` for setting up the connection to a Gen2 Azure blob storage account.

```
from DeltaAgent import DeltaAgent

da = DeltaAgent(account_name="account_name", account_key="account_key")
```

With the established connection agent, we can then parse the paths of valid parquet files and their corresponding partition information, by the method `parse_log_as_df`. The result is returned in the format of pandas DataFrame, with an additonal method `fetch_data`. At this stage we can perform inspections and the normal DataFrame `loc` method for efficient filtering operations.

```
df_log = da.parse_log_as_df(container_name='container_name', table_path='deltatable_name')

df_log_filtered = df_log.loc[df_log.partition=='partition_value']
```

By calling the `fetch_data` method on the above delta log DataFrame, we can fetch the actual data from a deltalake table.

```
df_delta = df_log_filtered.fetch_data()
```

Note that the values for `container_name` and `delta_table` can be also assigned when setting up the agent connection, as below:

```
da = DeltaAgent(account_name="account_name", account_key="account_key", container_name='container_name', table_path='deltatable_name')
```
