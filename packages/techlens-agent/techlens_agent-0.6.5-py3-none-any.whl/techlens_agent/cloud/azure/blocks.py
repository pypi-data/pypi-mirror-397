import datetime
import json
import os

from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsQueryClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import HttpResponseError

from techlens_agent.cloud.azure.cloud_helper import get_cloud_settings


def getBlocks(cloud_name: str, sub_id: str, path_to_output: str = "./", dry=False):
    if not dry:
        authority_constant, management_endpoint, cloud_setting, cred_scopes = (
            get_cloud_settings(cloud_name)
        )

        credential = DefaultAzureCredential(authority=authority_constant)
        client = MetricsQueryClient(credential, endpoint=management_endpoint)
        resource_client = ResourceManagementClient(
            credential,
            subscription_id=sub_id,
            cloud_setting=cloud_setting,
        )

        group_list = resource_client.resource_groups.list()
        storage_client = StorageManagementClient(
            credential,
            subscription_id=sub_id,
            cloud_setting=cloud_setting,
        )

        known_buckets = {}
        d = datetime.timedelta(days=1)
        for group in group_list:
            accounts = storage_client.storage_accounts.list_by_resource_group(
                resource_group_name=group.name
            )

            for account in accounts:
                # Skip accounts without a Blob endpoint (e.g., FileStorage)
                if not (
                    getattr(getattr(account, "primary_endpoints", None), "blob", None)
                ):
                    continue
                kind = getattr(account, "kind", "").lower()
                if not kind or kind not in [
                    "storage",
                    "storagev2",
                    "blockblobstorage",
                    "blobstorage",
                ]:
                    continue

                try:
                    containers = storage_client.blob_containers.list(
                        resource_group_name=group.name, account_name=account.name
                    )
                except HttpResponseError:
                    # Non-blob accounts can still slip through; skip gracefully
                    continue

                try:
                    o = client.query_resource(
                        resource_uri=account.id,
                        metric_names=["UsedCapacity"],
                        timespan=d,
                        metric_namespace="Microsoft.Storage/storageAccounts",
                        aggregations=["Average"],
                    )

                    used_bytes = (
                        o.metrics[0].timeseries[0].data[-1].average
                        if o.metrics
                        and o.metrics[0].timeseries
                        and o.metrics[0].timeseries[0].data
                        else None
                    )
                except HttpResponseError as e:
                    if "FeatureNotSupportedForAccount" in str(e):
                        used_bytes = None
                    else:
                        raise

                print(used_bytes)
                known_buckets[account.name] = {
                    "name": account.name,
                    "size": used_bytes,
                    "retention": None,
                    "public": False,
                    "permissions": [],
                }
                for c in containers:
                    if c.public_access:
                        known_buckets[account.name]["public"] = True
        my_buckets = list(known_buckets.values())
        upload = {
            "metadata": {"provider": "azure", "account": str(sub_id)},
            "data": my_buckets,
        }
    # End dry block
    azure_output_file = os.path.join(path_to_output, f"az-storage-{sub_id}.json")
    if not dry:
        with open(azure_output_file, "w") as outfile:
            outfile.write(json.dumps(upload, indent=4))
    return azure_output_file


# Test Code
# getBlocks(sub_id="80dc7a6b-df94-44be-a235-7e7ade335a3c")
